# AWS Lambda

## Commands

```bash
# build an image
docker buildx build --platform linux/amd64 --provenance=false -t 424432388155.dkr.ecr.ap-northeast-1.amazonaws.com/mexc/market-maker:0.1.0 .

# authe
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 424432388155.dkr.ecr.ap-northeast-1.amazonaws.com

# push image
docker push 424432388155.dkr.ecr.ap-northeast-1.amazonaws.com/mexc/market-maker:0.1.1

# invoke function
aws lambda invoke --region ap-northeast-1 --function-name market-maker /dev/stdout
```

## Steps

1. Sell evrything and keep only SOL
2. Build a python stanadlone bot
3. Update (lambda)
