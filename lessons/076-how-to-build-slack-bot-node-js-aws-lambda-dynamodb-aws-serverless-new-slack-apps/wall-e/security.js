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
