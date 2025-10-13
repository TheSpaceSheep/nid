from django.urls import path
from . import views

app_name = "demo"

urlpatterns = [
    path("", views.index, name="index"),
    path("send-notification/", views.send_notification, name="send_notification"),
]
