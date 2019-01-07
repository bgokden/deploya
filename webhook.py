from __future__ import print_function

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from github import Github, GithubException
import os
import shutil
from subprocess import call
import logging
import tempfile

logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s')

OWNER = os.environ['GITHUB_REPO_OWNER']
REPO_NAME = os.environ['GITHUB_REPO_NAME']
HOST = os.environ['SERVEO_SUBDOMAIN']+".serveo.net"
TOKEN = os.environ['GITHUB_TOKEN']
DOCKER_REPO = os.environ['DOCKER_REPO']
ENDPOINT = "webhook"
WORKSPACE = "/workspace"

@view_defaults(
    route_name=ENDPOINT, renderer="json", request_method="POST"
)
class PayloadView(object):
    """
    View receiving of Github payload. By default, this view it's fired only if
    the request is json and method POST.
    """

    def __init__(self, request):
        self.request = request
        # Payload from Github, it's a dict
        self.payload = self.request.json

    @view_config(header="X-Github-Event:push")
    def payload_push(self):
        """This method is a continuation of PayloadView process, triggered if
        header HTTP-X-Github-Event type is Push"""
        print("No. commits in push:", len(self.payload['commits']))
        self.processPush()
        return Response("success")

    @view_config(header="X-Github-Event:pull_request")
    def payload_pull_request(self):
        """This method is a continuation of PayloadView process, triggered if
        header HTTP-X-Github-Event type is Pull Request"""
        print("PR", self.payload['action'])
        print("No. Commits in PR:", self.payload['pull_request']['commits'])

        return Response("success")

    @view_config(header="X-Github-Event:ping")
    def payload_else(self):
        print("Pinged! Webhook created with id {}!".format(self.payload["hook"]["id"]))
        return {"status": 200}

    def processPush(self):
        try:
            print("ref", self.payload['ref'])
            print("hash", self.payload['before'])
            if self.payload['ref'] == "refs/heads/master" :
                print("Pushed to master")
                # git clone to workspace
                g = Github(TOKEN)
                repo = g.get_repo("{owner}/{repo_name}".format(owner=OWNER, repo_name=REPO_NAME))
                dirpath = tempfile.mkdtemp()
                logging.info("Working in directoy: "+dirpath)
                contents = repo.get_contents("", ref=self.payload['ref'])
                while len(contents) > 0:
                    file_content = contents.pop(0)
                    # print(file_content.path)
                    try:
                        if file_content.type == "dir":
                            contents.extend(repo.get_contents(file_content.path))
                        else:
                            logging.info(file_content)
                            folders_path = os.path.dirname(file_content.path)
                            if folders_path:
                                try:
                                    os.makedirs(dirpath+"/"+folders_path)
                                except OSError:
                                    pass
                            with open(dirpath+"/"+file_content.path, 'wb') as output:
                                output.write(file_content.decoded_content)
                    except Exception as e:
                        print(e) # this added due to a large file exception in get_contents
                # run kaniko
                docker_image = DOCKER_REPO+":"+self.payload['before']
                kubectl_files_folder=dirpath+"/kubernetes"
                # only run kaniko when dockerfile exists
                exists = os.path.isfile(dirpath+"/Dockerfile")
                if exists:
                    call(["/kaniko/executor", "-c", dirpath, "-d", docker_image])
                    call(["sed","-i", "s,IMAGE,"+docker_image+",g", kubectl_files_folder+"/deploy.yaml"])
                # run kubectl
                call(["kubectl","apply","-f", kubectl_files_folder])
                # clean
                shutil.rmtree(dirpath)
        except Exception as e:
            logging.error(e)


def create_webhook():
    """ Creates a webhook for the specified repository.

    This is a programmatic approach to creating webhooks with PyGithub's API. If you wish, this can be done
    manually at your repository's page on Github in the "Settings" section. There is a option there to work with
    and configure Webhooks.
    """

    EVENTS = ["push", "pull_request"]

    config = {
        "url": "https://{host}/{endpoint}".format(host=HOST, endpoint=ENDPOINT),
        "content_type": "json"
    }

    g = Github(TOKEN)
    repo = g.get_repo("{owner}/{repo_name}".format(owner=OWNER, repo_name=REPO_NAME))
    try:
        repo.create_hook("web", config, EVENTS, active=True)
    except GithubException as e:
        # Most of the time you already have the webhook
        print("Ignoring exception:",e)


if __name__ == "__main__":
    logging.info("main started")
    config = Configurator()

    create_webhook()

    config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
    config.scan()

    app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 8888, app)
    logging.info("serving on 0.0.0.0:8888")
    server.serve_forever()
