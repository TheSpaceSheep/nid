import random
import json
from django.shortcuts import render, redirect
from django.conf import settings
from config.constants import GREETINGS
from accounts.decorators import login_required
from accounts.models import get_user


@login_required
def index(request):
    """Home page that greets the logged in user"""
    user_name = request.COOKIES.get('user_name')
    user = get_user(user_name)

    if not user:
        return redirect('accounts:login')

    greeting = random.choice(GREETINGS)
    logout_messages = ['jme casse', 'ciao', 'je m\'en vais au revoir', 'me demande pas pq chuis parti sans motif']
    logout_message = random.choice(logout_messages)

    notifications_enabled_json = request.COOKIES.get('notifications_enabled', '{}')
    notifications_enabled = json.loads(notifications_enabled_json)

    return render(request, 'home/index.html', {
        'greeting': greeting,
        'user': user,
        'logout_message': logout_message,
        'notifications_enabled': notifications_enabled,
        'vapid_public_key': settings.VAPID_PUBLIC_KEY,
    })
