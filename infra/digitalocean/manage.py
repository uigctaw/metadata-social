#!/usr/bin/python3

from collections import defaultdict, namedtuple
from functools import lru_cache, wraps
import argparse
import inspect
import itertools
import os
import pathlib
import pprint
import re
import subprocess
import textwrap
import time
import uuid
import yaml

THIS_FOLDER = pathlib.Path().joinpath(__file__).parent


class Output:

    PUBLIC_IPS = 'public_ips'
    FIRST_MANAGER_NAME = 'first_manager_name'
    FIRST_WEBSITE_SERVER_NAME = 'first_website_server_name'
    MANAGER_NAMES = 'manager_names'
    WEBSITE_SERVERS_NAMES = 'website_servers_names'


parser = argparse.ArgumentParser()

parser.add_argument(
        '--do',
        action='store_true',
        help='Really execute: do not perform a dry run.',
        )
parser.add_argument(
        '--host-user',
        help='Needed for SSH connection.',
        )

_PROCEDURES = []


def procedure(fn):
    _PROCEDURES.append(fn)
    return fn


@lru_cache
def get_outputs():
    os.chdir(THIS_FOLDER)
    result = subprocess.run(
            ['terraform', 'output', '-json'],
            capture_output=True,
            )
    if result.stderr:
        raise RuntimeError(result.stderr)
    else:
        output = yaml.safe_load(result.stdout)
        return output


NameToIP = namedtuple('NameToIP', 'name ip')


def get_hosts():
    output = get_outputs()
    name_to_ip = tuple(itertools.starmap(
        NameToIP,
        output[Output.PUBLIC_IPS]['value'],
        ))
    return name_to_ip


def get_first_manager_name():
    output = get_outputs()
    return output[Output.FIRST_MANAGER_NAME]['value']


def get_first_website_server_name():
    output = get_outputs()
    return output[Output.FIRST_WEBSITE_SERVER_NAME]['value']


def get_website_servers_names():
    output = get_outputs()
    return tuple(output[Output.WEBSITE_SERVERS_NAMES]['value'])


def get_manager_names():
    output = get_outputs()
    return tuple(output[Output.MANAGER_NAMES]['value'])


StdOutStdErr = namedtuple('StdOutStdErr', 'stdout stderr')


def _get_exec(dry_run, target_user, args_getter):

    def _exec(*args):
        args = args_getter(*args)
        if dry_run:
            pprint.pprint(args)
            return StdOutStdErr('', '')
        else:
            result = subprocess.run(args, capture_output=True)
            out, err = result.stdout.decode(), result.stderr.decode()
            if out:
                print('STDOUT: ' + out)
            if err:
                print('STDERR: ' + err)
            return StdOutStdErr(out, err)

    return _exec


def get_ssh_exec(dry_run, target_user):

    def get_args(command, host):
        args = [
                'ssh',
                f'{target_user}@{host}',
                '-T',
                command,
        ]
        return args

    return _get_exec(dry_run, target_user, get_args)


def get_scp_exec(dry_run, target_user):

    def get_args(source_path, target_host, target_path):
        args = [
            'scp',
            source_path,
            f'{target_user}@{target_host}:{target_path}',
        ]
        return args

    return _get_exec(dry_run, target_user, get_args)


parser.add_argument(
        '--open-ports',
        action='store_true',
        help=(
                'Open ports necessary for Docker Swarm communication'
                ' between the hosts.'
                ),
        )
@procedure
def open_ports(dry_run, value, host_user, **_):
    if dry_run:
        print('DRY RUN')

    hosts = get_hosts()
    commands = defaultdict(list)
    for home, remote in itertools.permutations(hosts, 2):

        # https://docs.docker.com/engine/swarm/swarm-tutorial/#open-protocols-and-ports-between-the-hosts
        for port, protocol in [
                ('2377', 'tcp'),
                ('7946' ,'tcp'), 
                ('7946' ,'udp'), 
                ('4789' ,'udp'),
        ]:
            command = (
                    f'sudo ufw allow proto {protocol}'
                    f' from {remote.ip} to {home.ip} port {port}'
            )
            commands[home].append(command)

    def construct_command(commands):
        return 'set -e;\\\n%s;' % ';\\\n'.join(commands)


    ssh = get_ssh_exec(dry_run, host_user) 
    for host, command_collection in commands.items():
        command = construct_command(command_collection)
        ssh(command, host.ip)
    

parser.add_argument(
        '--ips', 
        action='store_true',
        help='Print existing ip addresses.',
        )
@procedure
def ips(*_):
    hosts = get_hosts()
    for host in hosts:
        print(host.name, host.ip)


parser.add_argument(
        '--first-manager-ip', 
        action='store_true',
        help='Print ip of the main/first manager.',
        )
@procedure
def first_manager_ip(*_):
    hosts = dict(get_hosts())
    first_manager_name = get_first_manager_name()
    print(hosts[first_manager_name])


parser.add_argument(
        '--swarm-init',
        action='store_true',
        help='Leave, create and join swarm.',
        )
@procedure
def swarm_init(dry_run, value, host_user):
    if dry_run:
        print('DRY RUN')

    hosts = dict(get_hosts())

    ssh_exec = get_ssh_exec(dry_run, host_user)

    resp = _destroy_swarm(ssh_exec, hosts.values())
    if resp.stderr:
        if bool(input(f'ERROR!\n`Enter` to continue')):
            return print('ABORTING')
    first_manager_name = get_first_manager_name()
    first_manager_ip = hosts[first_manager_name] 
    resp = _init_swarm(ssh_exec, first_manager_ip)
    if resp.stderr:
        if bool(input(f'ERROR!\n`Enter` to continue')):
            return print('ABORTING')
    other_managers_ips = (
            hosts[name] for name in get_manager_names()
            if name != first_manager_name
            )
    _join_swarm(ssh_exec, first_manager_ip, other_managers_ips)


def _join_swarm(ssh_exec, first_manager_ip, other_managers_ips):

    def join_command(what):
        print(f'Getting {what} join command from', first_manager_ip)
        join_command, = re.search(
                r'( docker swarm join --token .*)',
                ssh_exec(
                    f'docker swarm join-token {what}', 
                    first_manager_ip,
                ).stdout,
            ).groups()
        return join_command

    if dry_run:
        print('Exiting, cannot proceed when dry running.')
        return

    join_manager = join_command('manager')

    for manager_ip in other_managers_ips:
        print('Joining swarm: ', manager_ip)
        ssh_exec(join_manager, manager_ip)


def _destroy_swarm(ssh_exec, hosts):
    print('Destroying swarm on :', hosts)
    resps = []
    for host in hosts:
        resps.append(ssh_exec('docker swarm leave --force', host))
    out = '\n'.join(r.stdout for r in resps if r.stdout)
    err = '\n'.join(r.stderr for r in resps if r.stderr)
    return StdOutStdErr(out, err)

def _init_swarm(ssh_exec, ip):
    print('Initializing swarm on ', ip)
    return ssh_exec(
        f'docker swarm init --advertise-addr {ip}',
        ip,
        )


parser.add_argument(
        '--copy-certificate',
        help=(
            'Copy a TLS certificate from the specified location'
            + ' to all the server nodes.'
            )
        )
@procedure
def copy_certificate(dry_run, value, host_user):
    source_path = value
    hosts = dict(get_hosts())
    ssh_exec = get_ssh_exec(dry_run, host_user)
    scp_exec = get_scp_exec(dry_run, host_user)

    for website_server_name in get_website_servers_names():
        print('Running for ' + website_server_name)
        ip = hosts[website_server_name]
        # I suppose I should bring the node down first...
        cert_folder = '/srv/certs/live'
        temp_folder = f'~/temp/{uuid.uuid4().hex}'
        moved_cert_folder = f'/srv/certs/deleted/{time.time()}'
        ssh_exec(
            f'sudo mkdir -p {moved_cert_folder};'
            + f' sudo mv {cert_folder} {moved_cert_folder};'
            + f' mkdir -p {temp_folder};',
            ip, 
        )
        for file in ['chain.pem', 'fullchain.pem', 'privkey.pem']:
            scp_exec(
                    source_path + '/' + file,
                    ip,
                    f'{temp_folder}/',
                    )
        ssh_exec(
            f'sudo mkdir -p {cert_folder};'
            + f' sudo mv {temp_folder}/* {cert_folder};'
            + f' rmdir {temp_folder};',
            ip, 
        )
    print('DONE')


if __name__ == '__main__':
    args = parser.parse_args()
    kwargs = vars(args)
    dry_run = not kwargs.pop('do')
    called = [(proc, kwargs.pop(proc.__name__)) for proc in _PROCEDURES]
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    for proc, call_value in called:
        if call_value:
            proc(dry_run, call_value, **kwargs)

