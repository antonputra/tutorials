# How to Create Lambda Container Images?

- Build Docker Image

```
docker build -t app:v0.1.0 .
```

- Run Locally

```
docker run -p 7000:8080 app:v0.1.0
```

- Test Locally

```
curl -XPOST "http://localhost:7000/2015-03-31/functions/function/invocations" -d '{"name": "Anton"}'
```

- Remove All Locall docker containers and images

```
docker rm -vf $(docker ps -a -q) && docker rmi -f $(docker images -a -q)
```

- Tag Docker Image

```
docker tag app:v0.1.0 424432388155.dkr.ecr.us-east-1.amazonaws.com/app:v0.1.0
```

- Push Docker Image

```
docker push 424432388155.dkr.ecr.us-east-1.amazonaws.com/app:v0.1.0
```

- Add Jest

```
npm install --save-dev jest
```

- Run Tests

```
npm run test
```
