#!/bin/bash

set -e

for dir in ~/repos/metadata-social/components/*/
do
    echo $dir
    dir_no_trailing_slash=${dir%*/}
    container_name="${dir_no_trailing_slash##*/}"
    echo $container_name
    name_and_tag=uigctaw/metadata-social-$container_name:test
    echo Bulding $dir $name_and_tag
    sudo docker build "$dir" -t $name_and_tag
    echo Pushing $name_and_tag
    sudo docker push $name_and_tag
done
echo DONE
