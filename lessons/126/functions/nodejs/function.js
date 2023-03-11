const aws = require('aws-sdk');
const s3 = new aws.S3();
const ddb = new aws.DynamoDB({ apiVersion: '2012-08-10' });

// Download the S3 object and print content
const getS3Object = (bucket, key, callback) => {
    const params = {
        Bucket: bucket,
        Key: key
    };

    s3.getObject(params, (err, data) => {
        if (err) return err;
        console.log(data);
        callback(data.LastModified);
    });
};

// Save the item to the DynamoDB table
const save = (table, date, callback) => {
    const modifiedDate = date.toISOString()
    const params = {
        TableName: table,
        Item: { 'LastModified': { S: modifiedDate } }
    };

    ddb.putItem(params, (err, data) => {
        if (err) return err;
        callback(null, 200);
    });
};

// Returns a random number between min and max
const getRandomInt = (min, max) => {
    return Math.random() * (max - min) + min;
};

exports.lambda_handler = (event, context, callback) => {
    const bucket = process.env.BUCKET_NAME;
    const key = 'thumbnail.png';
    const table = 'Meta';

    getS3Object(bucket, key, (date) => {
        const randomNumberOfDays = getRandomInt(0, 100000);
        date.setDate(date.getDate() + randomNumberOfDays);
        save(table, date, callback);
    });
};