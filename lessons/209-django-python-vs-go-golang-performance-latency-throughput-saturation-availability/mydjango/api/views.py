import time
import uuid

import boto3
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from prometheus_summary import Summary

from .models import Image

s = Summary('myapp_request_duration_seconds', 'Duration of the request.', [
            'op'], invariants=((0.50, 0.05), (0.90, 0.01), (0.99, 0.001)))
s3_session = boto3.session.Session()
s3_client = s3_session.client('s3', endpoint_url=settings.S3['endpoint_url'])


def health(request):
    return HttpResponse("OK")


def devices(request):
    device = {
        'id': 1,
        'mac': '5F-33-CC-1F-43-82',
        'firmware': '2.1.6'
    }

    return JsonResponse(device)


def images(request):
    # Generate a new image.
    image_id = uuid.uuid4()
    created_at = timezone.now()
    obj_key = f'python-thumbnail-{str(image_id)}.png'

    img = Image(image_id, obj_key, created_at)

    # Upload the image to S3.
    start = time.time()

    with open(settings.S3['file_path'], 'rb') as data:
        s3_client.put_object(
            Body=data, Bucket=settings.S3['bucket'], Key=img.obj_key)

    s.labels(op='s3').observe(time.time() - start)

    # Save the image metadata to db.
    start = time.time()

    img.save()

    s.labels(op='db').observe(time.time() - start)

    return HttpResponse("Saved!")
