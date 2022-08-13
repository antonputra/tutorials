const AWS = require('aws-sdk')
const express = require('express')
const bodyParser = require('body-parser')

const app = express()
const port = 8080

app.use(bodyParser.json())

// Invoked when a client connects to the WebSocket API.
// It saves the current client connection ID to the DynamoDB database.
app.post('/connect', async (req, res) => {
    console.log('/connect endpoint is invoked')

    const tableName = req.body.tableName
    const region = req.body.region
    const connectionId = req.body.connectionId

    console.log('tableName:', tableName)
    console.log('region:', region)
    console.log('connectionId:', connectionId)

    const ddb = new AWS.DynamoDB.DocumentClient({ apiVersion: '2012-08-10', region: region })

    const putParams = {
        TableName: tableName,
        Item: { connectionId: connectionId }
    }

    try {
        await ddb.put(putParams).promise()
        console.info(`User with connection id: ${connectionId} joined the chat room.`)
        res.sendStatus(200)
    } catch (err) {
        console.error({ result: 'Failed to connect!', error: err })
        res.sendStatus(500)
    }
})

// Invoked when a client disconnects from the WebSocket API.
// It removes the current client connection ID from the DynamoDB database.
app.delete('/disconnect', async (req, res) => {
    console.log('/disconnect endpoint is invoked')

    const tableName = req.body.tableName
    const region = req.body.region
    const connectionId = req.body.connectionId

    console.log('tableName:', tableName)
    console.log('region:', region)
    console.log('connectionId:', connectionId)

    const ddb = new AWS.DynamoDB.DocumentClient({ apiVersion: '2012-08-10', region: region })

    const deleteParams = {
        TableName: tableName,
        Key: { connectionId: connectionId }
    }

    try {
        await ddb.delete(deleteParams).promise()
        console.info(`User with connection id: ${connectionId} left the chat room.`)
        res.sendStatus(200)
    } catch (err) {
        console.error({ result: 'Failed to connect!', error: err })
        res.sendStatus(500)
    }
})

// Invoked when a client sends a message to the chat room.
app.post('/sendmessage', async (req, res) => {
    console.log('/sendmessage endpoint is invoked')

    const tableName = req.body.tableName
    const region = req.body.region
    const connectionId = req.body.connectionId
    const domainName = req.body.domainName
    const stage = req.body.stage
    const postData = req.body.payload.message

    console.log('tableName:', tableName)
    console.log('region:', region)
    console.log('connectionId:', connectionId)
    console.log('domainName:', domainName)
    console.log('stage:', stage)
    console.log('postData:', postData)

    const ddb = new AWS.DynamoDB.DocumentClient({ apiVersion: '2012-08-10', region: region })

    let connectionData

    try {
        connectionData = await ddb.scan({ TableName: tableName, ProjectionExpression: 'connectionId' }).promise()
    } catch (e) {
        console.error({ result: 'Failed to connect!', error: e.stack })
        res.sendStatus(500)
        return
    }

    const apiEndpoint = domainName + '/' + stage
    console.log('API Endpoint:', apiEndpoint)

    const apigwManagementApi = new AWS.ApiGatewayManagementApi({
        apiVersion: '2018-11-29',
        region: region,
        endpoint: apiEndpoint
    })

    const postCalls = connectionData.Items.map(async ({ connectionId }) => {
        try {
            await apigwManagementApi.postToConnection({ ConnectionId: connectionId, Data: postData }).promise()
        } catch (e) {
            if (e.statusCode === 410) {
                console.log(`Found stale connection, deleting ${connectionId}`)
                await ddb.delete({ TableName: tableName, Key: { connectionId } }).promise()
            } else {
                throw e
            }
        }
    })

    try {
        await Promise.all(postCalls)
        console.log(`A message to the client with connection id: ${connectionId} is sent.`)
        res.sendStatus(204)
    } catch (e) {
        console.error({ result: 'Failed!', error: e.stack })
        res.sendStatus(500)
    }
})

app.listen(port, () => {
    console.log(`App listening on port ${port}`)
})
