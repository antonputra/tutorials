# AWS SAM

[YouTube Tutorial](https://youtu.be/sK9-aKUOmYE)

## 1. Install AWS SAM CLI
- [Instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
### macOS
```
brew tap aws/tap
```
```
brew install aws-sam-cli
```
```
sam --version
```

## 2. Setting up AWS credentials

- Create `admin` user for AWS SAM
- Download Credentials
- Configure AWS Cli
```
aws configure
```

## 3. Create AWS Lambda API Gateway Node JS
- Initialize SAM project
```
sam init
```
- Go over project structure
- Remove generated project
```
rm -rf sam
```
- Created `sam` directory
- Create `api` directory
- Change directory to `api`
```
cd sam/api
```
- Run `npm init`
```
npm init
```
- Create a `function.js` file
- Create `template.yaml` file
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: AWS SAM Tutorial

Globals:
  Function:
    MemorySize: 128

Resources:
  APIFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs14.x
      Handler: function.lambdaHandler
      CodeUri: api/
      Timeout: 3
      Events:
        Hello:
          Type: Api
          Properties:
            Path: /hello
            Method: POST
            RestApiId: 
              Ref: HelloAPI

  HelloAPI:
    Type: AWS::Serverless::Api
    Properties:
      StageName: staging
      OpenApiVersion: 3.0.3

Outputs:
  APIFunction:
    Description: "Api Lambda Function ARN"
    Value: !GetAtt APIFunction.Arn
  Tutorials:
    Description: "YouTube Channel"
    Value: https://www.youtube.com/antonputra
```

## 4. Test Lambda Locally SAM

- Change directory to `sam`
- Run `sam build`
- Create `api/event.json`
- `sam local invoke APIFunction -e api/event.json`
- Run `sam deploy --guided`
- Go to S3
- Get URL from console
```
curl -d '{"name": "Anton"}' https://jh7n04hpaj.execute-api.us-east-1.amazonaws.com/staging/hello
```

## 5. Test Lambda from Console
- Create new `TestName` event
```json
{
  "body": "{\"name\": \"Anton\"}"
}
```

## Create AWS Lambda S3 File Upload NodeJS
- Create `s3` folder
- Run `npm init` from `s3` folder
- Create `function.js` file
- Install aws-sdk `npm i aws-sdk` 
- Add S3Function, ExampleBucket and Outputs
- Run `sam build`
- Run `sam deploy`
- Go to S3
- Fo to lambda
- Upload README to S3
- Go to CloudWatch

## Create AWS Lambda SNS Python Example
- Create `sns` folder
- Create `function.py`, `requirements.txt`, and `Dockerfile`
- Add `SNSFunction` and `Outputs`
- Create SNS topic `sns-topic-for-lambda`
- Run `sam build`
- Run `sam deploy --guided`
- Create ECR repo `sns`
- Publish message
- Check CloudWatch logs

## Clen Up

 - Delete SNS topic `sns-topic-for-lambda`
 - Delete ECR repository `sns`
 - Delete all cloud watch log groups
 - Delete IAM User `admin`
 - Delete AWS CLI `sam`
 ```
 brew remove aws-sam-cli
 ```
 - Delete all S3 buckets
 - Delete all CloudFormation Templates
