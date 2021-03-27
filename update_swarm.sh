#!/bin/bash

set -e

ROOT=$1

INFRA_MANAGER=$ROOT/infra/digitalocean/manage.py
FIRST_MANAGER_IP=$($INFRA_MANAGER --first-manager-ip)
scp $ROOT/components/docker-stack.yaml mdsdckr@$FIRST_MANAGER_IP:
ssh mdsdckr@$FIRST_MANAGER_IP -T "\
    docker stack deploy -c docker-stack.yaml mdsstack; \
    "
