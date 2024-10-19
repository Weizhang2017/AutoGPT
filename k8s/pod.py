from kubernetes import client, config

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
