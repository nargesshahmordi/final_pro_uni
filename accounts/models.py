from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

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
