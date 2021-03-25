#!/bin/bash

set -e

INFRA_MANAGER=./infra/digitalocean/manage.py
FIRST_MANAGER_IP=$($INFRA_MANAGER --first-manager-ip)
scp ./components/docker-stack.yaml mdsdckr@$FIRST_MANAGER_IP:
ssh mdsdckr@$FIRST_MANAGER_IP -T "\
    docker stack deploy -c docker-stack.yaml mdsstack; \
    "
