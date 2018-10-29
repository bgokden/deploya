#!/usr/bin/env bash

echo "Serving on $SERVEO_SUBDOMAIN.serveo.net"
autossh -f -o StrictHostKeyChecking=no -M 0 -R $SERVEO_SUBDOMAIN:80:localhost:8888 serveo.net

kubectl config set-cluster cfc --server=https://kubernetes.default --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

kubectl config set-context cfc --cluster=cfc

TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
USER_ID=default

kubectl config set-credentials $USER_ID --token=$TOKEN

kubectl config set-context cfc --user=$USER_ID

kubectl config use-context cfc

kubectl get secret reposecret --output="jsonpath={.data.\.dockerconfigjson}" -n $PULL_SECRET_NAMESPACE | base64 -d > /kaniko/.docker/config.json

echo "Running webhook"
exec python /app/webhook.py
