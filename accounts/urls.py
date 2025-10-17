from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("handle-login/", views.handle_login, name="handle_login"),
    path("logout/", views.logout, name="logout"),
]
