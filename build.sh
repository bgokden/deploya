#!/usr/bin/env bash

VERSION=0.1.15

IMAGE=berkgokden/deploya:$VERSION

docker build -t $IMAGE .
docker push $IMAGE

echo $IMAGE
