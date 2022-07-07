const aws = require('aws-sdk');

const s3 = new aws.S3({ apiVersion: '2006-03-01' });

exports.handler = async (event, context) => {
    console.log('Received event:', JSON.stringify(event, null, 2));

    const bucket = event.bucket;
    const object = event.object;
    const key = decodeURIComponent(object.replace(/\+/g, ' '));

    const params = {
        Bucket: bucket,
        Key: key,
    };
    try {
        const { Body } = await s3.getObject(params).promise();
        const content = Body.toString('utf-8');
        return content + ' works!!!';
    } catch (err) {
        console.log(err);
        const message = `Error getting object ${key} from bucket ${bucket}.`;
        console.log(message);
        throw new Error(message);
    }
};
