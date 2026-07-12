from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from apps.common.models import BaseModel   

from .managers import UserManager

phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید با فرمت 09xxxxxxxxx باشه',
)


class User(AbstractUser):
    """
    کاربر سفارشی پروژه.
    تصمیم: به‌جای username از phone_number به‌عنوان شناسه‌ی ورود استفاده می‌کنیم
    (رایج‌ترین روش لاگین برای اپ‌های ساختمانی در ایران).
    نقش کاربر در هر ساختمان جدا مدل می‌شه (BuildingMembership) — نه اینجا،
    چون یک کاربر می‌تونه در ساختمان‌های مختلف نقش‌های متفاوت داشته باشه.
    """
    username = None
    email = models.EmailField(blank=True, null=True)

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='شماره موبایل',
    )
    national_code = models.CharField(
        max_length=10, blank=True, null=True, verbose_name='کد ملی'
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/', blank=True, null=True, verbose_name='آواتار'
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []  # createsuperuser فقط phone_number و password می‌پرسه

    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.get_full_name() or self.phone_number


# ... کلاس User همون قبلیه ...

class BuildingMembership(BaseModel):
    """
    نقش یک کاربر در یک ساختمان مشخص.
    عمداً روی خود User نگذاشتیم چون یک نفر می‌تونه هم‌زمان:
    - در ساختمان A مدیر باشه
    - در ساختمان B فقط مالک/ساکن باشه
    """
    class Role(models.TextChoices):
        MANAGER = 'manager', 'مدیر ساختمان'
        BOARD_MEMBER = 'board_member', 'عضو هیئت مدیره'
        OWNER = 'owner', 'مالک'
        TENANT = 'tenant', 'مستاجر'
        STAFF = 'staff', 'کارمند / سرایدار'

    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='memberships', verbose_name='کاربر'
    )
    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='memberships', verbose_name='ساختمان'
    )
    role = models.CharField(max_length=20, choices=Role.choices, verbose_name='نقش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        unique_together = ('user', 'building', 'role')
        verbose_name = 'عضویت در ساختمان'
        verbose_name_plural = 'عضویت‌ها در ساختمان'

    def __str__(self):
        return f"{self.user} - {self.building} - {self.get_role_display()}"