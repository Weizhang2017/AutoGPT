kubectl delete -f autogpt_job.yml
docker build -f Dockerfile_autogpt_job . -t auto-gpt-job:0.1
docker tag auto-gpt-job:0.1 localhost:5001/auto-gpt-job:0.1
docker push localhost:5001/auto-gpt-job:0.1
kubectl apply -f autogpt_job.yml