#!/bin/bash

set -e

USAGE="
1) 

-v --version : release candidate version


Optional parameters:

-h --help : Displays this documentation.

-r --root : `cd` to this directory at the start. Defaults to `pwd`.
"

while [[ $# -gt 0 ]]; do
    case $1 in 
        -v|--version) VERSION=$2; shift;;
        -r|--root) ROOT=$2; shift;;
        -h|--help) HELP=1;;
        *) UNHANDLEDED_PARAMETER=$1;;
    esac
    if [[ $UNHANDLEDED_PARAMETER != "" ]]; then
        echo "I do not understand $UNHANDLEDED_PARAMETER"
        echo "Type -h for help"
    fi
    shift
done

if [[ $HELP == "1" ]]; then
    echo "$USAGE"
    exit 0
fi

if [[ $VERSION == "" ]]; then
    echo "Missing -v"
    echo "Type -h for help"
    exit 1
fi

if [[ $ROOT == "" ]]; then
    ROOT=$(pwd)
fi
             
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo Version should be in a form '"<int>.<int>.<int>"'
    echo where '"<int>"' is a positive integer.
    exit 1
fi

VERSION_FILE=version

CURRENT=$(<$VERSION_FILE)

if [[ $(echo -e "$CURRENT" | head -n1) == CRASHED ]]; then
    echo 'Looks like a previous release crashed. Please fix manually.'
    exit 1
fi

if [[ 
        $VERSION = $(echo -e "$VERSION\n$CURRENT" | sort -V | head -n1)
        || $VERSION == $CURRENT
]]; then
    echo The new version "($VERSION)" must be bigger than the current version,
    echo i.e. $CURRENT 
    exit 1
fi

LOG=release.log

function log {
    echo $VERSION $1 | tee -a $LOG
}

cd $ROOT

log 'Messing up the version file'
echo -e "CRASHED\n$CURRENT" > $VERSION_FILE

log 'Switching to "main" branch'
git checkout main

log 'Running tests'
./test.sh  

log 'Creating stack file'
./components/stack_file_generator.py --version $VERSION

log 'Committing, tagging and pushing code'
git commit
git tag -a v$VERSION -m "Deployment, v$VERSION" 
git push origin v$VERSION

log 'Building and pushing images'
./components/build_and_push_images.sh $VERSION $ROOT

log DEPLOYING!
update_swarm.sh $ROOT

log 'Writing new version file'
echo $VERSION > $VERSION_FILE

log DONE
