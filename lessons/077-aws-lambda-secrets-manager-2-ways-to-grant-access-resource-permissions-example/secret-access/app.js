const AWS = require('aws-sdk'),
    region = "us-east-1",
    secretName = "prod/slack-bot/token-v3";

const client = new AWS.SecretsManager({
    region: region
});

const getSecret = (secretName, callback) => {
    let secret, decodedBinarySecret;
    client.getSecretValue({ SecretId: secretName }, (err, data) => {
        if (err) {
            callback(null, { message: err.message });
        }
        else {
            if ('SecretString' in data) {
                secret = data.SecretString;
            } else {
                let buff = new Buffer(data.SecretBinary, 'base64');
                decodedBinarySecret = buff.toString('ascii');
            }
        }
        callback(null, secret);
    });
};

exports.handler = (event, context, callback) => {
    getSecret(secretName, callback);
};
