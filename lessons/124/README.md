# AWS Lambda Go vs. Node.js performance benchmark

- Compile go code for Lambda

```bash
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o main main.go
```

- Run load test

```bash
loadtest \
    --concurrency 5 \
    --maxRequests 1000 \
    --rps 10 \
    --keepalive \
    https://<your-id>.lambda-url.us-east-1.on.aws/
```
