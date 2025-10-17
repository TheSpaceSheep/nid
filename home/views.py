import random
from django.shortcuts import render, redirect
from constants import GREETINGS
from accounts.decorators import login_required
from accounts.models import User


@login_required
def index(request):
    """Home page that greets the logged in user"""
    user_name = request.COOKIES.get('user_name')
    try:
        user = User.objects.get(name=user_name)
    except User.DoesNotExist:
        return redirect('accounts:login')

    greeting = random.choice(GREETINGS)
    logout_messages = ['jme casse', 'ciao', 'je m\'en vais au revoir', 'me demande pas pq chuis parti sans motif']
    logout_message = random.choice(logout_messages)

    return render(request, 'home/index.html', {
        'greeting': greeting,
        'user': user,
        'logout_message': logout_message,
    })
