from .threadlocal import set_current_user, clear_current_user


class CurrentUserMiddleware:
    """
    سیگنال‌های Django (post_save/post_delete) به request دسترسی ندارن.
    این میدلور کاربر لاگین‌شده رو توی thread-local می‌ذاره تا signals.py
    بتونه actor رو توی AuditLog ثبت کنه.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        set_current_user(user if user and user.is_authenticated else None)
        try:
            response = self.get_response(request)
        finally:
            clear_current_user()
        return response
