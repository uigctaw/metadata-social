#!/bin/python3

import argparse
import pathlib
import string
from html_builder import html_builder

TEMPLATE = f'''
version: "3.7"
services:
  backend:
    image: uigctaw/metadata-social-nginx:{{version}}
    deploy:
      mode: global
    volumes:
      - nginx_content:/usr/share/nginx/html
      - type: bind
        source: /srv/certs/live
        target: /srv/certs/live

    ports:
      - 443:443
  app:
    image: uigctaw/metadata-social-pyapp:{{version}}
    deploy:
      mode: global
    volumes:
      - nginx_content:{html_builder.STATIC_FILES_DIR}
volumes:
    nginx_content:
'''

TARGET_FILE_NAME = pathlib.Path(__file__).parent.joinpath('docker-stack.yaml')


class TemplateFormatter(string.Formatter):

    def check_unused_args(self, used_args, args, kwargs):
        if args:
            raise ValueError('Passing args is not supported: %s' % (args,))

        diff = set(kwargs) - used_args

        if diff:
            raise RuntimeError('The template does not need %s ' % (diff,))


def write(string):
    with open(TARGET_FILE_NAME, 'w') as fh:
        fh.write(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help='Version tags of images')
    args = parser.parse_args()
    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    formatted = TemplateFormatter().format(TEMPLATE, **kwargs)
    write(formatted)
