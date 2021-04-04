import boto3

s3 = boto3.client('s3')

print('Original Object:')
original = s3.get_object(
  Bucket='devopsbyexample-object-lambda',
  Key='title.txt')
print(original['Body'].read().decode('utf-8'))

print('Processed Object:')
transformed = s3.get_object(
  Bucket='arn:aws:s3-object-lambda:us-east-1:424432388155:accesspoint/title-transform',
  Key='title.txt')
print(transformed['Body'].read().decode('utf-8'))
