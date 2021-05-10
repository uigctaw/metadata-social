#!/bin/bash

set -e

ROOT=$(pwd)/$(dirname $0)
          
cd $ROOT/components/html_builder
poetry run pytest
cd $ROOT
