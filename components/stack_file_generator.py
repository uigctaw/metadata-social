#!/bin/python3

import argparse
import pathlib
import string
import textwrap

TEST_VERSION = 'test'


class MetaConfig(type):
    """Stricly enforce what attributes config can have."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if cls.__name__ != 'Config':
            extra_attributes = set(vars(cls)) - set(vars(Config))
            public_extra_attrs = [
                ea for ea in extra_attributes if not ea.startswith('_')
            ]
            missing_attributes = set(vars(Config)) - {
                    k for k, v in vars(cls).items() if v is not NotImplemented
            }
            public_missing_attrs = [
                ma for ma in missing_attributes if not ma.startswith('_')
            ]
            if public_extra_attrs:
                raise AttributeError(
                    '{cls} has extra attributes: %s' % public_extra_attrs       
                )
            if public_missing_attrs:
                raise AttributeError(
                    f'{cls} is missing attributes: %s' % public_missing_attrs
                )
        return cls


class Config(metaclass=MetaConfig):
    
    nginx_img = NotImplemented
    nginx_port_binding = NotImplemented
    docker_file_name = NotImplemented
    html_builder_img = NotImplemented
    nginx_bind_certs = NotImplemented


class Test(Config):

    nginx_img = 'nginx'
    nginx_port_binding = '8080:80'
    docker_file_name = 'docker-compose.yaml'
    html_builder_img = 'html_builder:{version}'
    nginx_bind_certs = False


class Prod(Config):

    nginx_img = 'uigctaw/metadata-social-nginx:{version}'
    nginx_port_binding = '443:443'
    docker_file_name = 'docker-stack.yaml'
    html_builder_img = 'uigctaw/metadata-social-html_builder:{version}'
    nginx_bind_certs = True


DELETE_LINE_COMMENT = '# <delete>'


def get_docker_filer(config, *, version):
    maybe_delete = '' if config.nginx_bind_certs else DELETE_LINE_COMMENT

    base = textwrap.dedent(f'''
    version: "3.7"
    services:
      backend:
        image: {config.nginx_img}
        deploy:
          mode: global
        volumes:
          - nginx_content:/usr/share/nginx/html
          - type: bind              {maybe_delete}   
            source: /srv/certs/live {maybe_delete}   
            target: /srv/certs/live {maybe_delete}   

        ports:
          - {config.nginx_port_binding}
      app:
        image: {config.html_builder_img}
        deploy:
          mode: global
        volumes:
          - nginx_content:/data
    volumes:
        nginx_content:
    ''')
    with_lines_to_delete = TemplateFormatter().format(base, version=version)
    formatted = '\n'.join(
            line
            for line in 
            with_lines_to_delete.splitlines()
            if not line.strip().endswith(DELETE_LINE_COMMENT)
            )
    return formatted


ROOT = pathlib.Path(__file__).parent


class TemplateFormatter(string.Formatter):

    def check_unused_args(self, used_args, args, kwargs):
        if args:
            raise ValueError('Passing args is not supported: %s' % (args,))

        diff = set(kwargs) - used_args

        if diff:
            raise RuntimeError('The template does not need %s ' % (diff,))


def write(config, string):
    with open(ROOT.joinpath(config.docker_file_name), 'w') as fh:
        fh.write(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--version', help='Version tags of images', required=True,
            )
    args = parser.parse_args()
    version = args.version
    config = Test if version == TEST_VERSION else Prod
    file = get_docker_filer(config, version=version)
    write(config, file)
