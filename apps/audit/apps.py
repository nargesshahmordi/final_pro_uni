from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'
    label = 'audit'

    def ready(self):
        # سیگنال‌ها اینجا وصل می‌شن تا از مرحله ۱ (به قول نقشه‌راه: مرحله ۳ که audit
        # فعال می‌شه) روی همه‌ی appهای بعدی که ثبت می‌کنیم به‌صورت خودکار کار کنه.
        from . import signals  # noqa: F401
