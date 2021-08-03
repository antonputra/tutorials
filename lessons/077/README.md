# AWS Lambda Secrets Manager Example: 2 Ways to Grant Access | Resource Permissions

[YouTube Tutorial](https://youtu.be/_VI2JkSo3DY)

## 1. Create Secret in AWS Secrets Manager
- Create `SLACK_BOT_TOKEN` secret with random value
- Give it a name `prod/slack-bot/token-v3`

## 2. Create IAM User with Full Access
- Create `admin` user and place it in `Admin` IAM group
- Configure aws cli `aws configure`

## 3. Create IAM Role for AWS Lambda
- Create IAM Policy `AWSLambdaSecretsAccess`
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:us-east-1:424432388155:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:us-east-1:424432388155:log-group:/aws/lambda/secret-access:*"
        }
    ]
}
```
- Create `secret-access-role` IAM Role

## 4. Create AWS Lambda Function
- Create `secret-access` folder
- Run `npm init`
- Install aws-sdk `npm i aws-sdk`
- Create `app.js`
- Create `Dockerfile`

## 5. Deploy Lambda Using Container Image
- Create ECR `secret-access`
- Build and push image
```
aws ecr get-login-password --region us-east-1 | \
docker login --username AWS \
--password-stdin 424432388155.dkr.ecr.us-east-1.amazonaws.com
```
```bash
docker build -t 424432388155.dkr.ecr.us-east-1.amazonaws.com/secret-access:v0.1.0 .
```
```bash
docker push 424432388155.dkr.ecr.us-east-1.amazonaws.com/secret-access:v0.1.0
```
- Deploy lambda
- Test with curl (fail)

## 6. Grant Access for IAM Role
```json
{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:us-east-1:424432388155:secret:prod/slack-bot/token-v3-<id>"
}
```
- Remove access

## 7. Create Resource-based Policy for Secret
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:sts::424432388155:assumed-role/secret-access-role/secret-access"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:424432388155:secret:prod/slack-bot/token-v3-<id>"
    }
  ]
}
```

## Clean UP
- Delete `admin` IAM user
- Delete ECR `secret-access`
- Delete `secret-access-role` IAM Role
- Delete `AWSLambdaSecretsAccess` IAM Policy
- Delete `secret-access` lambda
- Delete `secret-access-API` API gateway
- Delete CloudWatch logs
- Delete secrets

## Links
[Resource-based policies](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_resource-policies.html)  
[AWS JSON policy elements: Principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html)  
