from functools import wraps
from django.shortcuts import redirect


def login_required(view_func):
    """Decorator to require a valid user cookie"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        user_name = request.COOKIES.get('user_name')
        if not user_name:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapped_view
