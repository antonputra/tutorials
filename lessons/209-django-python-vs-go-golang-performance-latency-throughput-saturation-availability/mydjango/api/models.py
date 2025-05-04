from django.db import models


class Image(models.Model):
    image_id = models.UUIDField(primary_key=True)
    obj_key = models.CharField(max_length=256)
    created_at = models.DateTimeField()
