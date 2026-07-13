from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AuditLog(models.Model):
    """
    لاگ فقط-اضافه‌شونده (append-only). عمداً از BaseModel ارث‌بری نمی‌کنه:
    - خودش نباید soft-delete بشه (لاگ که پاک‌شدنی نیست).
    - نباید توسط signals خودش دوباره audit بشه (ریسک recursion).
    """
    class Action(models.TextChoices):
        CREATE = 'create', 'ایجاد'
        UPDATE = 'update', 'ویرایش'
        DELETE = 'delete', 'حذف'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name='کاربر انجام‌دهنده',
    )
    action = models.CharField(max_length=10, choices=Action.choices, verbose_name='نوع عملیات')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='نوع مدل')
    object_id = models.CharField(max_length=255, verbose_name='شناسه رکورد')
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, verbose_name='نمایش رکورد در زمان لاگ')

    # دنورمالایز عمدی: خیلی از گزارش‌ها/دسترسی‌ها per-building هستن،
    # بدون این فیلد هر بار باید از content_object مسیر رو دنبال کرد.
    building = models.ForeignKey(
        'buildings.Building',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name='ساختمان',
    )

    changes = models.JSONField(
        default=dict, blank=True,
        verbose_name='تغییرات',
        help_text='برای update: {field: [قدیم, جدید]} — برای create: مقادیر اولیه',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        verbose_name = 'رخداد audit'
        verbose_name_plural = 'رخدادهای audit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['building', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.object_repr} - {self.created_at:%Y-%m-%d %H:%M}"
