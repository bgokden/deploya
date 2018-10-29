# deploya

Deploya is a tool for easy managing kubernetes deployment.
It is currently a Proof of Concept how Kaniko can be used for in-cluster builds.
See Project Kaniko: https://github.com/GoogleContainerTools/kaniko

* Deploya automatically connects to a github repo webhook.
* Clones the github repo and builds it with Kaniko and pushed image to the docker repo
* deploys your new image to the cluster

how to use:

Open an account on: https://hub.docker.com/
Generate a github personal access token: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/

Configure environment variable in deploya.yaml

And then run the commands below:

kubectl create namespace continuous-deployment
kubectl create secret docker-registry reposecret --docker-server=https://index.docker.io/v1/ --docker-username=<username> --docker-password=<password> --docker-email=<email> -n continuous-deployment
kubectl create namespace deploya-system
kubectl create secret generic github-token-secret --from-literal=token=<github-token> -n deploya-system

kubectl apply -f deploya.yaml

See the github repo: https://github.com/bgokden/flask-hello-world/
It has a folder called kubernetes with a file called deploy.yaml
And it has a Dockerfile
It is expected that the project is dockerized.

Every time there is a push to master, project will be deployed in the cluster.

I will try to write a longer explanation and I will try to simplify the process.
