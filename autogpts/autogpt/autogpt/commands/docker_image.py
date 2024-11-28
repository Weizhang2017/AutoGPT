from autogpt.command_decorator import command
import logging
from pathlib import Path
import docker
from autogpt.core.utils.json_schema import JSONSchema
from autogpt.agents.agent import Agent

COMMAND_CATEGORY = "docker_image"
COMMAND_CATEGORY_TITLE = "Docker Image"


logger = logging.getLogger(__name__)

@command(
    "build_docker_image",
    "build a docker image and push image to registry localhost:5001",
    {
        "Dockerfile_path": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The path of the file to read",
            required=True,
        ),
        'tag': JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The tag of the image",
            required=True,
        ),
    },
)
def create_docker_image(Dockerfile_path: str | Path, agent: Agent, tag: str):
    # import pdb;pdb.set_trace()
    if Dockerfile_path == '.':
        Dockerfile_path = './Dockerfile'
        path = str(agent.workspace.root)
    elif len(Dockerfile_path.split('/')) > 1:
        path = str(agent.workspace.root) + '/' + '/'.join(Dockerfile_path.split('/')[:-1])
        Dockerfile_path = Dockerfile_path.split('/')[-1]
    else:
        path = str(agent.workspace.root) + '/' + Dockerfile_path
        Dockerfile_path = './Dockerfile'
    registry = 'localhost:5001'
    client = docker.from_env()
    if registry in tag:
        tag = tag.split('/')[-1]
    resp = client.images.build(path=path, dockerfile=Dockerfile_path, tag=tag)
    image = client.images.get(tag)
    repository = f'{registry}/{tag}'
    image.tag(repository=repository)
    resp = client.images.push(repository=repository)
    return f'Image {tag} created'
