import os
import datetime
import random
import boto3

bucket = os.getenv('BUCKET_NAME')
key = 'thumbnail.png'
table = 'Meta'

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


# Download the S3 object and return last modified date
def get_s3_object(bucket, key):
    object = s3.get_object(Bucket=bucket, Key=key)
    object_content = object['Body'].read()
    print(object_content)
    return object['LastModified']


# Save the item to the DynamoDB table
def save(table, date):
    table = dynamodb.Table(table)
    table.put_item(Item={'LastModified': date.isoformat()})


# Lambda handler
def lambda_handler(event, context):
    date = get_s3_object(bucket, key)
    random_number_of_days = random.randint(0, 100000)
    date += datetime.timedelta(days=random_number_of_days)
    save(table, date)
