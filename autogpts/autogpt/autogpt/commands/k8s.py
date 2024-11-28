from kubernetes import client, config
from kubernetes.client import V1Deployment, V1DeploymentSpec, V1PodTemplateSpec, V1ObjectMeta, V1Container, V1ContainerPort, V1LabelSelector, V1PodSpec, V1Service, V1ServiceSpec, V1ServicePort, V1ServiceAccount, V1Namespace, V1ObjectMeta
from autogpt.command_decorator import command
import logging
from autogpt.core.utils.json_schema import JSONSchema
from autogpt.agents.agent import Agent



COMMAND_CATEGORY = "k8s"
COMMAND_CATEGORY_TITLE = "k8s commands"


logger = logging.getLogger(__name__)


class Pod:

    def __init__(self, pvc_name, pod_name, namespace='default'):

        self.config = config.load_incluster_config()

        persistent_volume_claim = client.V1Volume(
            name="my-pvc",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
        )

        volume_mount = client.V1VolumeMount(
            name="my-pvc",
            mount_path="/mnt/persistent"
        )


        container = client.V1Container(
            name="my-container",
            image="localhost:5001/auto-gpt-test:0.2",
            command=["/bin/sh", "-c", "echo Hello, Kubernetes! && sleep 3600"],
            volume_mounts=[volume_mount]
        )

        # Define the Pod spec
        pod_spec = client.V1PodSpec(
            containers=[container],
            service_account_name="my-service-account",  # Attach the ServiceAccount
            volumes=[persistent_volume_claim]
        )

        # Define the Pod metadata
        metadata = client.V1ObjectMeta(name=pod_name, namespace="default")

        # Create the Pod object
        self.pod = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=pod_spec
        )

        # Create an API client for interacting with Pods
        self.v1 = client.CoreV1Api()

        # Create the Pod in the specified namespace
        self.namespace = namespace

    def create_pod(self):
        response = self.v1.create_namespaced_pod(namespace=self.namespace, body=self.pod)

        # Print the name of the created Pod
        print(f"Pod created: {response.metadata.name}")
        return response



class Deployment:
    
    registry = 'localhost:5001'

    def __init__(self, app_name, image, container_port=5000, namespace='default'):
        self.config = config.load_incluster_config() #load_config()
        self.app_name = app_name
        if self.registry not in image:
            self.image = f'{self.registry}/{image}'
        else:
            self.image = image
        self.container_port = container_port
        self.namespace = namespace

    def create_deployment(self):
        # Container specification
        container = V1Container(
            name=self.app_name,
            image=self.image,  # Replace with your image
            ports=[V1ContainerPort(container_port=self.container_port)]
        )

        # Pod template specification
        template = V1PodTemplateSpec(
            metadata=V1ObjectMeta(labels={"app": self.app_name}),
            spec=V1PodSpec(containers=[container])
        )

        # Deployment specification
        spec = V1DeploymentSpec(
            replicas=1,  # Define the number of replicas you want
            selector=V1LabelSelector(match_labels={"app": self.app_name}),
            template=template
        )

        # Create the deployment object
        deployment = V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=V1ObjectMeta(name=f"{self.app_name}-deployment"),
            spec=spec
        )

        # Create the deployment in Kubernetes
        apps_v1 = client.AppsV1Api()
        response = apps_v1.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment
        )

        return "Deployment created. Status='%s'" % response.metadata.name

# Create a service to expose the Flask app
class Service:

    def __init__(self, service_name, app_name, port, target_port, namespace='default'):
        self.config = config.load_incluster_config() # load_config()
        self.service_name = service_name
        self.app_name = app_name
        self.port = port
        self.target_port = target_port
        self.namespace = namespace

    def create_nodeport_service(self):
        # Define the service with NodePort
        service = V1Service(
            api_version="v1",
            kind="Service",
            metadata=V1ObjectMeta(name=self.service_name),
            spec=V1ServiceSpec(
                selector={"app": self.app_name},
                ports=[V1ServicePort(
                    protocol="TCP",
                    port=self.port,          # service port
                    target_port=self.target_port,  # Container port
                )],
                type="NodePort"  # Service type is NodePort
            )
        )

        # Create the service in Kubernetes
        core_v1 = client.CoreV1Api()
        response = core_v1.create_namespaced_service(
            namespace=self.namespace,
            body=service
        )

        return f"NodePort Service created. Name: '{response.metadata.name}', NodePort: {response.spec.ports[0].node_port}"


@command(
    "create_k8s_deployment",
    "create a kubernetes deployment",
    {
        "app_name": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="deployment name",
            required=True,
        ),
        'image': JSONSchema(
            type=JSONSchema.Type.STRING,
            description="deployment image",
            required=True,
        ),
        'container_port': JSONSchema(
            type=JSONSchema.Type.INTEGER,
            description="container port",
            required=False,
        ),
        'namespace': JSONSchema(
            type=JSONSchema.Type.STRING,
            description="deployment namespace",
            required=True,
        ),
    },
)
def create_deployment(app_name, image, container_port, namespace, agent):
    create_namespace_if_not_exist(namespace)
    deployment = Deployment(app_name, image, container_port, namespace)
    resp = deployment.create_deployment()
    return resp


@command(
    "create_k8s_service",
    "create a kubernetes service",
    {
        "service_name": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="service name",
            required=True,
        ),
        'app_name': JSONSchema(
            type=JSONSchema.Type.STRING,
            description="deployment name",
            required=True,
        ),
        'port': JSONSchema(
            type=JSONSchema.Type.INTEGER,
            description="service port",
            required=True,
        ),
        'target_port': JSONSchema(
            type=JSONSchema.Type.INTEGER,
            description="container port",
            required=True,
        ),
        'namespace': JSONSchema(
            type=JSONSchema.Type.STRING,
            description="deployment namespace",
            required=True,
        ),
    },
)
def create_service(service_name, app_name, port, target_port, namespace, agent):
    create_namespace_if_not_exist(namespace)
    service = Service(service_name, app_name, port, target_port, namespace)
    resp = service.create_nodeport_service()
    return resp


@command(
    "create_k8s_namespace",
    "create a kubernetes namespace",
    {
        "namespace": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="create a namespace",
            required=True,
        ),
    },
)
def create_namespace(namespace, agent):
    # Create a namespace object
    namespace_body = V1Namespace(
        metadata=V1ObjectMeta(name=namespace)
    )
    config.load_incluster_config() # load_config()
    # Create the namespace using the CoreV1Api
    core_v1 = client.CoreV1Api()
    try:
        response = core_v1.create_namespace(body=namespace_body)
        print(f"Namespace '{response.metadata.name}' created successfully.")
        return f"Namespace '{response.metadata.name}' created successfully."
    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.info(f"Namespace '{namespace}' already exists.")
            return f"Namespace '{namespace}' already exists."
        else:
            raise Exception(f"Exception when creating namespace: {e}")


def list_namespaces():
    config.load_incluster_config() #load_config()
    # Use the CoreV1Api to list namespaces
    core_v1 = client.CoreV1Api()
    try:
        namespace_list = []
        namespaces = core_v1.list_namespace()
        for ns in namespaces.items:
            namespace_list.append(ns.metadata.name)
        return namespace_list
    except Exception as e:
        raise Exception(f"Error listing namespaces: {e}")

def create_namespace_if_not_exist(namespace):
    namespaces = list_namespaces()
    if namespace not in namespaces:
        create_namespace(namespace, agent=None)
        return f'namespace {namespace} created'
    else:
        return f'namespace {namespace} exists'

