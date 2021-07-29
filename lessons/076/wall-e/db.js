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
