from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("handle-login/", views.handle_login, name="handle_login"),
    path("logout/", views.logout, name="logout"),
    path("password/", views.enter_password, name="enter_password"),
    path("handle-password/", views.handle_password, name="handle_password"),
]
