"""
Middleware that forces a password change on first login.
"""
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """
    While a user has ``must_change_password`` set, every page redirects to the
    change-password form. The form itself, logout, and static files stay
    reachable so the user is never locked into a redirect loop.

    Must be listed after AuthenticationMiddleware so ``request.user`` exists.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user is not None and user.is_authenticated and getattr(user, 'must_change_password', False):
            change_url = reverse('accounts:password_change')
            exempt = {change_url, reverse('accounts:logout'), '/admin/logout/'}

            if request.path not in exempt and not request.path.startswith(settings.STATIC_URL):
                return redirect(change_url)

        return self.get_response(request)
