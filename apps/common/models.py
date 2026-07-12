from django.db import models
from django.utils import timezone

from .managers import ActiveManager


class BaseModel(models.Model):
    """
    مدل پایه‌ای که همه‌ی مدل‌های اصلی پروژه باید ازش ارث‌بری کنن.
    شامل: تایم‌استمپ، ثبت کاربر ایجادکننده، و soft-delete.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ آخرین ویرایش')
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name='ایجادکننده',
    )
    is_deleted = models.BooleanField(default=False, verbose_name='حذف‌شده')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ حذف')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
