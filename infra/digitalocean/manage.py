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
import yaml

THIS_FOLDER = pathlib.Path().joinpath(__file__).parent

FIRST_MANAGER = 'cluster-lon-a'
ADDITIONAL_MANAGERS = ('cluster-lon-b', 'cluster-ams-a')
ADDITIONAL_WORKERS = ()


parser = argparse.ArgumentParser()
parser.add_argument(
        '--ips', 
        action='store_true',
        help='Print existing ip addresses.',
        )
parser.add_argument(
        '--open-ports',
        action='store_true',
        help=(
                'Open ports necessary for Docker Swarm communication'
                ' between the hosts.'
                ),
        )
parser.add_argument(
        '--do',
        action='store_true',
        help='Really execute: do not perform a dry run.',
        )
parser.add_argument(
        '--host-user',
        help='Needed for SSH connection.',
        )
parser.add_argument(
        '--swarm-init',
        action='store_true',
        help=(
            'Leave, create and join swarm as specified in the script itself.'
            f' FIRST_MANAGER: {FIRST_MANAGER}'
            f' ADDITIONAL_MANAGERS: {ADDITIONAL_MANAGERS}'
            f' ADDITIONAL_WORKERS: {ADDITIONAL_WORKERS}'
            ),
        )

NameToIP = namedtuple('NameToIP', 'name ip')

_PROCEDURES = []


def procedure(fn):

    @wraps(fn)
    def wrapped(*args, **kwargs):
        none_args = [a for a in args if a is None]
        none_kwargs = [k for k, v in kwargs.items() if v is None and k != '_']
        none_any = none_args + none_kwargs
        spec = inspect.getfullargspec(fn)
        none_any = set(none_any) & set(spec.args + spec.kwonlyargs)
        if none_any:
            none_any = [x.replace('_', '-') for x in none_any]
            raise ValueError(f'You must supply: {none_any}' )
        return fn(*args, **kwargs)

    _PROCEDURES.append(wrapped)

    return wrapped
        


@lru_cache
def get_hosts():
    os.chdir(THIS_FOLDER)
    result = subprocess.run(
            ['terraform', 'output', '-json'],
            capture_output=True,
            )
    if result.stderr:
        raise RuntimeError(result.stderr)
    else:
        output = yaml.safe_load(result.stdout)
        name_to_ip = tuple(itertools.starmap(
            NameToIP,
            output['public_ips']['value'],
            ))
        return name_to_ip


def get_ssh(dry_run, host_user):

    def ssh(command, host):
        args = [
                'ssh',
                f'{host_user}@{host}',
                '-T',
                command,
        ]
        if dry_run:
            pprint.pprint(args)
            return ''
        else:
            result = subprocess.run(args, capture_output=True)
            print('STDOUT: ' + result.stdout.decode())
            print('STDERR: ' + result.stderr.decode())
            return result.stdout.decode()

    return ssh


@procedure
def open_ports(dry_run, host_user, **_):
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


    ssh = get_ssh(dry_run, host_user) 
    for host, command_collection in commands.items():
        command = construct_command(command_collection)
        ssh(command, host.ip)
    

@procedure
def ips(_, **__):
    hosts = get_hosts()
    for host in hosts:
        print(host.name, host.ip)


@procedure
def swarm_init(dry_run, host_user):
    hosts = dict(get_hosts())
   

    ssh = get_ssh(dry_run, host_user)

    for host in hosts.values():
        ssh('docker swarm leave --force', host)

    _1st_manager_ip = hosts[FIRST_MANAGER] 
    ssh(
            f'docker swarm init --advertise-addr {_1st_manager_ip}',
            _1st_manager_ip,
            )

    def join_command(what):
        join_command, = re.search(
                r'( docker swarm join --token .*)',
                ssh(f'docker swarm join-token {what}', _1st_manager_ip),
                ).groups()
        return join_command

    if dry_run:
        print('Exiting, cannot proceed when dry running.')
        return

    join_worker = join_command('worker')
    join_manager = join_command('manager')

    for manager in ADDITIONAL_MANAGERS:
        ssh(join_manager, hosts[manager])

    for worker in ADDITIONAL_WORKERS:
        ssh(join_worker, hosts[worker])


if __name__ == '__main__':
    args = parser.parse_args()
    kwargs = vars(args)
    dry_run = not kwargs.pop('do')

    if dry_run: 
        print('DRY RUN')

    for proc in [
        proc for proc in _PROCEDURES
        if kwargs.pop(proc.__name__, False)
    ]:
        proc(dry_run, **kwargs)

