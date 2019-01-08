FROM gcr.io/kaniko-project/executor:v0.7.0
FROM python:3.6-alpine3.8

COPY --from=0 /kaniko /kaniko

ENV HOME /root
ENV USER /root

RUN apk update && \
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/community/" >> /etc/apk/repositories && \
    apk add --update autossh bash git && \
    rm -rf /var/lib/apt/lists/*

# Note: Latest version of kubectl may be found at:
# https://aur.archlinux.org/packages/kubectl-bin/
ENV KUBE_LATEST_VERSION="v1.10.2"
# Note: Latest version of helm may be found at:
# https://github.com/kubernetes/helm/releases
ENV HELM_VERSION="v2.9.1"

RUN apk add --no-cache ca-certificates bash git \
    && wget -q https://storage.googleapis.com/kubernetes-release/release/${KUBE_LATEST_VERSION}/bin/linux/amd64/kubectl -O /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && wget -q http://storage.googleapis.com/kubernetes-helm/helm-${HELM_VERSION}-linux-amd64.tar.gz -O - | tar -xzO linux-amd64/helm > /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm


# ENTRYPOINT ["/kaniko/executor"]

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh
COPY requirements.txt /app/
RUN cd app && pip install -r requirements.txt
COPY webhook.py /app/

ENV PATH="/kaniko:${PATH}"
ENV SSL_CERT_DIR=/kaniko/ssl/certs
ENV DOCKER_CONFIG /kaniko/.docker/
WORKDIR /workspace

# ENV SERVEO_SUBDOMAIN berk

CMD ["/entrypoint.sh"]
