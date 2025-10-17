import random
import hmac
import hashlib
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from config.constants import GREETINGS
from .models import USERS, VALID_USER_NAMES, get_user
from .decorators import login_required


def login(request):
    """Login page with random greeting and user selection buttons"""
    greeting = random.choice(GREETINGS)
    return render(request, 'accounts/login.html', {
        'greeting': greeting,
        'users': USERS,
    })


@require_http_methods(["POST"])
def handle_login(request):
    """Handle user login by setting a persistent cookie"""
    user_name = request.POST.get('name', '').strip()

    if not user_name or user_name not in VALID_USER_NAMES:
        return redirect('accounts:login')

    response = redirect('home:index')
    response.set_cookie(
        'user_name',
        user_name,
        max_age=31536000,  # 1 year in seconds
        httponly=True,
        samesite='Lax'
    )
    return response


def logout(request):
    """Clear the user cookie and redirect to login"""
    response = redirect('accounts:login')
    response.delete_cookie('user_name')
    return response


def enter_password(request):
    """Display password entry form"""
    return render(request, 'accounts/password_prompt.html')


@require_http_methods(["POST"])
def handle_password(request):
    """Handle password submission and set authentication cookie"""
    password = request.POST.get('password', '').strip()
    site_password = settings.SITE_PASSWORD

    if password == site_password:
        # Generate secure token
        token = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=site_password.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        response = redirect(request.GET.get('next', 'accounts:login'))
        response.set_cookie(
            'site_password_token',
            token,
            max_age=31536000,  # 1 year in seconds
            httponly=True,
            samesite='Lax'
        )
        return response

    # Password incorrect - show form again with error
    return render(request, 'accounts/password_prompt.html', {
        'error': 'Incorrect password. Try again.'
    }, status=401)
