let response;

exports.lambdaHandler = async (event, context) => {
    try {
        const body = JSON.parse(event.body);
        response = {
            'statusCode': 200,
            'body': `Hello ${body.name}!`,
        };
    } catch (err) {
        console.log(err);
        return err;
    }
    return response
};
