# How to Build Slack Bot? (Node JS | AWS Lambda & DynamoDB - AWS Serverless | New Slack Apps)

[YouTube Tutorial](https://youtu.be/rUIptoPXu_8)

## 1. Create Slack Bot App
- Go to https://api.slack.com/apps
- Select create an app `From scratch`
- Give it a name `WALL-E` and select your namespace
- Scroll down to `App Credentials` a `Display Information`
- Give it a short description `Compactor robot`
- Upload app icon and change color
- Go to `Event Subscriptions`

## 2. Create IAM User with Full Access
- Create `admin` user and place it in `Admin` group
- Download credentials
- Configure AWS profile with `aws configure`
- Test profile with `aws sts get-caller-identity`

## 3. Create IAM Role for AWS Lambda
- Create IAM Policy `AWSLambdaSlackAccess`
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
            "Resource": "arn:aws:logs:us-east-1:424432388155:log-group:/aws/lambda/wall-e:*"
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:*",
            "Resource": "arn:aws:dynamodb:us-east-1:424432388155:table/todos"
        }
    ]
}
```
- Create `wall-e-role` for Lambda and attach `AWSLambdaSlackAccess` IAM Policy
- Optionally: `aws iam get-role --role-name wall-e-role`

## 4. Create AWS Lambda Function
- Create `wall-e` directory
- Run `npm init` from `wall-e` directory
- Create `app.js`
```javascript
exports.handler = (event, context, callback) => {
    const response = { 'message': `Hello World!` };
    callback(null, response);
};
```
- Create `Dockerfile`
```
FROM public.ecr.aws/lambda/nodejs:14

COPY *.js package*.json  /var/task/

RUN npm install

CMD [ "app.handler" ]
```
- Create ECR Repository `wall-e`
```bash
aws ecr get-login-password --region us-east-1 \
| docker login \
--username AWS \
--password-stdin 424432388155.dkr.ecr.us-east-1.amazonaws.com
```
```
docker build \
-t 424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.0 .
```
```
docker push \
424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.0
```
## 5. Deploy Lambda Using Container Image
- Select `Containerimage` from the console
- Call function `wall-e`
- Use an existing role `wall-e-role`
- Select `wall-e` ECR image

## 6. Create API Gateway for Lambda Function
- Create HTTP API `slack`
- Test Lambda with curl
```
curl -X POST https://uss0o5l3h3.execute-api.us-east-1.amazonaws.com/production/wall-e
```
- Check logs
- Use this URL for Slack

## 7. Use AWS Lambda for Slack Event Subscriptions
- Create `tests/event.json` file
```json
{
  "version": "2.0",
  "routeKey": "ANY /bot",
  "rawPath": "/default/bot",
  "rawQueryString": "",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip,deflate",
    "content-length": "129",
    "content-type": "application/json",
    "host": "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
    "user-agent": "Slackbot 1.0 (+https://api.slack.com/robots)",
    "x-amzn-trace-id": "Root=1-60f9f121-0e6b301236f5d57d46fbd0e1",
    "x-forwarded-for": "3.94.92.68",
    "x-forwarded-port": "443",
    "x-forwarded-proto": "https",
    "x-slack-request-timestamp": "1626992929",
    "x-slack-signature": "v0=d12f7cb55add77074248241c2ec2d3c9fe4611e7879a965c92315edd8f0ec0cf"
  },
  "requestContext": {
    "accountId": "424432388155",
    "apiId": "4o68t2fwke",
    "domainName": "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
    "domainPrefix": "4o68t2fwke",
    "http": {
      "method": "POST",
      "path": "/default/bot",
      "protocol": "HTTP/1.1",
      "sourceIp": "3.94.92.68",
      "userAgent": "Slackbot 1.0 (+https://api.slack.com/robots)"
    },
    "requestId": "C5KdVjAlIAMEPzg=",
    "routeKey": "ANY /bot",
    "stage": "default",
    "time": "22/Jul/2021:22:28:49 +0000",
    "timeEpoch": 1626992929961
  },
  "body": "{\"token\":\"UdG3UFNsPGoobvRzK5F2oIqe\",\"challenge\":\"6KaNtlamllYYaLZ7qhHxZbzyYut62TlDKu2wAZXp4rZlInRbcDTH\",\"type\":\"url_verification\"}",
  "isBase64Encoded": false
}
```
- Update body of the function
```javascript
exports.handler = (event, context, callback) => {
    const body = JSON.parse(event.body);
    switch (body.type) {
        case "url_verification": callback(null, body.challenge); break;
        default: callback(null);
    }
};
```
- Package and upload docker image
```
docker build \
-t 424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.1 .
```
```
docker push \
424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.1
```
- Redeploy AWS Lambda using v0.1.1 image tag
- Go back to Slack and click `Retry`

## 8. Verify Slack Requests Using Signing Secret
- Optionally: Create verify.js
- Run with `node verify.js`
- Compare string with event.json
- Create `security.js`
```javascript
const crypto = require("crypto");

exports.validateSlackRequest = (event, signingSecret) => {
    const requestBody = event["body"];
    const headers = makeLower(event.headers);
    const timestamp = headers["x-slack-request-timestamp"];
    const slackSignature = headers["x-slack-signature"];
    const baseString = 'v0:' + timestamp + ':' + requestBody;

    const hmac = crypto.createHmac("sha256", signingSecret)
        .update(baseString)
        .digest("hex");
    const computedSlackSignature = "v0=" + hmac;
    const isValid = computedSlackSignature === slackSignature;

    return isValid;
};

const makeLower = (headers) => {
    let lowerCaseHeaders = {}

    for (const key in headers) {
        if (headers.hasOwnProperty(key)) {
            lowerCaseHeaders[key.toLowerCase()] = headers[key].toLowerCase()
        }
    }

    return lowerCaseHeaders
}
```
- Update `app.js`
```javascript
const security = require('./security');

const signingSecret = process.env.SLACK_SIGNING_SECRET;

exports.handler = (event, context, callback) => {
    if (security.validateSlackRequest(event, signingSecret)) {
        const body = JSON.parse(event.body);
        switch (body.type) {
            case "url_verification": callback(null, body.challenge); break;
            default: callback(null);
        }
    }
    else callback("verification failed");
};
```
- Add Environment variable to Lambda `SLACK_SIGNING_SECRET` (next video aws lambda secrets manager integration)
- Create unit test `security.test.js`
- Install Jest `npm i --save-dev jest`
- Update test command to `jest`
- Run tests `npm test`

## 9. Process Slack Messages
- Create private Slack channel `earth`
- Subscribe to following events
  - message.groups
  - message.channels
- Install app to workspace
- Optionally: set `Always Show My Bot as Online` from `App Home`
- Go to `OAuth & Permissions` to check automatically added permissions
- Add `event_callback` event
```javascript
case "event_callback": processRequest(body, callback); break;
```
- Create `processRequest` method
```javascript
const processRequest = (body, callback) => {
    switch (body.event.type) {
        case "message": processMessages(body, callback); break;
        default: callback(null);
    }
};
```
- Create `processMessages` method in `app.js`
```javascript
const processMessages = (body, callback) => {
    console.debug("message:", body.event.text);
    callback(null);
};
```
- Update `Dockerfile` to use `npm ci --production`
- Package and upload docker image
```
docker build \
-t 424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.2 .
```
```
docker push \
424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.2
```
- Update AWS Lambda to use `v0.1.2` tag
- Optionally: Delete all log streams
- Inviite `WALL-E` to `earth` channel
- Post `hello` message
- Open CloudWatch logs

## 10. Save Messages Using AWS Lambda to DynamoDB
- Create `todos` DynamoDB table with `uuid` primary key
- Replace `message.groups` and `message.channels` with `app_mention` event
- Add `chat:write` instead of `message.*`
- Reinstall app
- Install `aws-sdk`, `uuid`, and `axios`
```bash
npm i aws-sdk uuid axios
```
- Create `db.js`
```javascript
const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');

AWS.config.update({ region: 'us-east-1' });

const ddb = new AWS.DynamoDB({ apiVersion: '2012-08-10' });

exports.saveItem = (item, callback) => {
    const params = {
        TableName: 'todos',
        Item: {
            'uuid': { S: uuidv4() },
            'item': { S: item }
        }
    };
    ddb.putItem(params, (error, data) => {
        if (error) {
            callback(new Error(error));
        } else {
            callback(null);
        }
    });
};
```
- Add `app_mention` case
```javascript
case "app_mention": processAppMention(body, callback); break;
```
- Import `axios` and `db`
```javascript
const axios = require('axios');
const db = require('./db');
```
- Create `token` variable and add it to Lambda
```javascript
const token = process.env.SLACK_BOT_TOKEN;
```
- Create `processAppMention` method
```javascript
const processAppMention = (body, callback) => {
    const item = body.event.text.split(":").pop().trim();
    db.saveItem(item, (error, result) => {
        if (error !== null) {
            callback(error)
        } else {
            const message = {
                channel: body.event.channel,
                text: `Item: \`${item}\` is saved to *Amazon DynamoDB*!`
            };
            axios({
                method: 'post',
                url: 'https://slack.com/api/chat.postMessage',
                headers: { 'Content-Type': 'application/json; charset=utf-8', 'Authorization': `Bearer ${token}` },
                data: message
            })
                .then((response) => {
                    callback(null);
                })
                .catch((error) => {
                    callback("failed to process app_mention");
                });
        }
    });
};
```
- Package and upload docker image
```
docker build \
-t 424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.3 .
```
```
docker push \
424432388155.dkr.ecr.us-east-1.amazonaws.com/wall-e:v0.1.3
```
- Redeploy Lambda using `v0.1.3` tag
- Post `@WALL-E todo: Save the Planet!` message
- Open DynamoDB `todos` table

## Clean Up
- Delete ECR `wall-e`
- Delete IAM User `admin`
- Delete IAM Role `wall-e-role`
- Delete IAM Policy `AWSLambdaSlackAccess`
- Delete DynamoDB table `todos`
- Delete Lambda `wall-e`
- Delete CloudWatch log groups `/aws/lambda/wall-e`
- Delete API Gateway `slack`
- Delete docker images `docker rmi -f $(docker images -a -q)`
- Delete slack bot `wall-e`
- Delete `earth` Slack channel

## Links
- [Basic app setup](https://api.slack.com/authentication/basics)
- [Signing secrets](https://api.slack.com/authentication/verifying-requests-from-slack)
- [Features - Choosing between HTTP APIs and REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)
- [HTTP API Price](https://aws.amazon.com/about-aws/whats-new/2019/12/amazon-api-gateway-offers-faster-cheaper-simpler-apis-using-http-apis-preview/)
- [Validating Library for Node JS](https://nodejs.org/api/crypto.html#crypto_crypto_createhmac_algorithm_key_options)
- [Verify Requst from Slack](https://api.slack.com/authentication/verifying-requests-from-slack)
- [chat.postMessage](https://api.slack.com/methods/chat.postMessage)
