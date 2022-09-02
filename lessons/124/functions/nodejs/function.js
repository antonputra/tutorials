const aws = require('aws-sdk');
aws.config.update({ region: 'us-east-1' });
const s3 = new aws.S3();
const ddb = new aws.DynamoDB({ apiVersion: '2012-08-10' });

exports.handler = function (event, context, callback) {
    var s3Params = {
        Bucket: process.env.BUCKET_NAME,
        Key: 'thumbnail.png'
    };

    s3.getObject(s3Params, function (err, data) {
        if (err) return err;
        console.log(data);

        const dbParams = {
            TableName: 'Meta',
            Item: { 'LastModified': { S: data.LastModified.toString() + Math.random() } }
        };
        ddb.putItem(dbParams, function (err, data) {
            if (err) return err;
            console.log("Success", data);
            callback(null, 200);
        });
    });
};
