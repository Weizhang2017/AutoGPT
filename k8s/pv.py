from kubernetes import client, config


class PV:
    def __init__(self, pvc_name, namespace='default'):

        # Load kube config (can be set to load from in-cluster or kubeconfig file)
        self.config = config.load_incluster_config()  # Use this for local environment using kubeconfig

        # Create a V1PersistentVolumeClaim object
        self.pvc = client.V1PersistentVolumeClaim(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata=client.V1ObjectMeta(name=pvc_name),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=client.V1ResourceRequirements(
                    requests={"storage": "128Mi"}
                ),
                storage_class_name="local-path"
            )
        )

        # Create an API client for interacting with PVCs
        self.v1 = client.CoreV1Api()

        # Create the PVC in a specific namespace (e.g., "default")
        self.namespace = namespace

    def create_pv(self):
        response = self.v1.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=self.pvc)

        # Print out the response
        print(f"PVC created. Status: {response.status.phase}")
        return response


