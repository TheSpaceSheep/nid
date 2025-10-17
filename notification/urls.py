from django.urls import path
from . import views

app_name = "notification"

urlpatterns = [
    path("send-notification/", views.send_notification, name="send_notification"),
    path("save-subscription/", views.save_subscription, name="save_subscription"),
]
