from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
import hmac
import hashlib
from django.conf import settings


class PasswordProtectionMiddleware(MiddlewareMixin):
    """
    Simple middleware that protects the entire site with a password prompt.
    Once a user enters the correct password, they receive a secure cookie
    that identifies them as trusted, and won't be prompted again.
    """

    PROTECTED_PATHS = [
        "/accounts/",
        "/home/",
        "/notification/",
    ]

    def _get_password_token(self):
        """Generate a secure token from the site password."""
        password = settings.SITE_PASSWORD
        return hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=password.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

    def process_request(self, request):
        # Check if user already has valid password cookie
        token = self._get_password_token()
        if request.COOKIES.get("site_password_token") == token:
            return None

        # Allow password prompt page and password submission
        exempt_paths = [
            reverse("accounts:enter_password"),
            reverse("accounts:handle_password"),
        ]
        if request.path in exempt_paths:
            return None

        # Check if this path should be protected
        for protected_path in self.PROTECTED_PATHS:
            if request.path.startswith(protected_path):
                return render(request, "accounts/password_prompt.html", status=401)

        return None
