import boto3
import requests


def lambda_handler(event, context):
    print(event)
    
    object_get_context = event["getObjectContext"]
    request_route = object_get_context["outputRoute"]
    request_token = object_get_context["outputToken"]
    s3_url = object_get_context["inputS3Url"]

    # Get object from S3
    response = requests.get(s3_url)
    original_object = response.content.decode('utf-8')

    # Transform object
    transformed_object = original_object.upper()

    # Write object back to S3 Object Lambda
    s3 = boto3.client('s3')
    s3.write_get_object_response(
        Body=transformed_object,
        RequestRoute=request_route,
        RequestToken=request_token)
    return {'status_code': 200}
