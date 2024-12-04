# Copyright (c) Microsoft Corporation
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for full license information.

#!/bin/bash

cd $(dirname $0)/..

echo "Current working directory before setting the ROOT_FOLDER: $(pwd)"

EXEC="docker buildx"

USER="yinfangchen"

TAG="buggy"

# ENTER THE ROOT FOLDER
cd ../
ROOT_FOLDER=$(pwd)
echo "ROOT_FOLDER: $(pwd)"
$EXEC create --name mybuilder --use

for i in geo #frontend geo profile rate recommendation reserve search user #uncomment to build multiple images
do
  IMAGE=${i}
  echo Processing image ${IMAGE}
  cd $ROOT_FOLDER
  $EXEC build -t "$USER"/"$IMAGE":"$TAG" -f Dockerfile . --platform linux/arm64,linux/amd64 --push
  cd $ROOT_FOLDER

  echo
done


cd - >/dev/null
