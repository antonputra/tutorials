from django.urls import path

from . import views

urlpatterns = [
    path("devices", views.devices, name="devices"),
    path("images", views.images, name="images"),
    path("healthz", views.health, name="health"),
]
