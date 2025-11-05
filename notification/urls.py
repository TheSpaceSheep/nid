from django.urls import path
from . import views

app_name = "notification"

urlpatterns = [
    path("send-notification/", views.send_notification, name="send_notification"),
    path("save-subscription/", views.save_subscription, name="save_subscription"),
    path("enable-poubelle/", views.enable_poubelle_notifications, name="enable_poubelle"),
    path("disable-poubelle/", views.disable_poubelle_notifications, name="disable_poubelle"),
    path("send-poubelle-reminders/", views.send_poubelle_reminders, name="send_poubelle_reminders"),
]
