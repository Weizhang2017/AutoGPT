#### Create docker image

```shell
cd autogpts/autogpt/
docker build . -t auto-gpt-test:0.1
```
#### Add OPENAI_API_KEY into env_config.yml file

#### Deploy auto-gpt as a pod on K8s to serve a frontend
```shell
cd k8s/
kubectl apply -f .
```

#### Access the frontend at http://localhost:30000

