#!/bin/bash

VERSION=$1
ROOT=$2

set -e

for dir in $ROOT/components/*/
do
    echo $dir
    dir_no_trailing_slash=${dir%*/}
    container_name="${dir_no_trailing_slash##*/}"
    echo $container_name
    name_and_tag=uigctaw/metadata-social-$container_name:$VERSION
    echo Bulding $dir $name_and_tag
    sudo docker build "$dir" -t $name_and_tag
    echo Pushing $name_and_tag
    sudo docker push $name_and_tag
done
echo DONE
