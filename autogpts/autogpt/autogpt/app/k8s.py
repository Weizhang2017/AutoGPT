from kubernetes import client, config
from kubernetes.client import V1Container, V1VolumeMount, V1Volume, V1HostPathVolumeSource, V1PodSpec, V1Deployment, V1DeploymentSpec, V1Service, V1ServiceSpec

def create_deployment(task, namespace="agent-space"):
    
    config.load_kube_config()
    api_instance = client.AppsV1Api()
    # Define container
    container = V1Container(
        name="agent-container",
        image="localhost:5001/auto-gpt-test:0.4",  # Replace with your container image
        ports=[client.V1ContainerPort(container_port=80)],
        command=["/bin/sh", "-c", f"./autogpt.sh run --gpt4only --task='{task}'"],
        volume_mounts=[
            V1VolumeMount(
                name="host-volume",
                mount_path="/var/run/docker.sock"  # Mount path inside the container
            )
        ]
    )

    volume = V1Volume(
        name="host-volume",
        host_path=V1HostPathVolumeSource(
            path="/var/run/docker.sock",  # Path on the host machine
        )
    )

    # Define pod template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "agent-app"}),
        spec=V1PodSpec(containers=[container], service_account_name="my-service-account", volumes=[volume]
)
    )

    # Define deployment spec
    spec = V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": "agent-app"}),
        template=template
    )

    # Define deployment object
    deployment = V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="agent-deployment"),
        spec=spec
    )

    # Create deployment
    api_instance.create_namespaced_deployment(namespace='agent-space', body=deployment)
    print("Deployment created successfully.")

def create_service(namespace="agent-space"):
    
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    node_port = 30001
    # Define service spec
    spec = V1ServiceSpec(
        type="NodePort",
        selector={"app": "agent-app"},
        ports=[
            client.V1ServicePort(port=80, target_port=80, node_port=node_port)
        ]
    )

    # Define service object
    service = V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name="agent-service"),
        spec=spec
    )

    # Create service
    api_instance.create_namespaced_service(namespace='agent-space', body=service)
    print("Service created successfully.")
    return node_port

def main():
    # config.load_incluster_config()  # For in-cluster setup (inside a pod)

    namespace = "agent-space"  # Set your namespace

    # Create Deployment and Service
    create_deployment(namespace)
    create_service(namespace)

if __name__ == "__main__":
    main()
