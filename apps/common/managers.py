from django.db import models


class ActiveManager(models.Manager):
    """
    فقط رکوردهای soft-delete نشده رو برمی‌گردونه.
    استفاده‌ی پیش‌فرض روی مدل: objects = ActiveManager()
    برای دسترسی به رکوردهای حذف‌شده هم: all_objects = models.Manager()
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
