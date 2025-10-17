import random
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from constants import GREETINGS
from .models import User
from .decorators import login_required


def login(request):
    """Login page with random greeting and user selection buttons"""
    # Ensure all users exist
    user_names = [
        ("noe", "Noé"),
        ("baz", "Baz"),
        ("philo", "Philo"),
        ("maya", "Maya"),
        ("jules", "Jules"),
        ("clotilde", "Clotilde"),
        ("pierre", "Pierre"),
        ("lorene", "Lorene"),
    ]
    for name, _ in user_names:
        User.objects.get_or_create(name=name)

    greeting = random.choice(GREETINGS)
    users = User.objects.all()
    return render(request, 'accounts/login.html', {
        'greeting': greeting,
        'users': users,
    })


@require_http_methods(["POST"])
def handle_login(request):
    """Handle user login by setting a persistent cookie"""
    user_name = request.POST.get('name', '').strip()

    if not user_name:
        return redirect('accounts:login')

    try:
        user = User.objects.get(name=user_name)
    except User.DoesNotExist:
        return redirect('accounts:login')

    response = redirect('home:index')
    response.set_cookie(
        'user_name',
        user.name,
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
