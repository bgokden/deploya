#!/usr/bin/env bash

VERSION=0.1.13

IMAGE=berkgokden/deploya:$VERSION

docker build -t $IMAGE .
docker push $IMAGE

echo $IMAGE
