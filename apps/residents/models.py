from django.core.validators import RegexValidator
from django.db import models

from apps.common.models import BaseModel

phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید با فرمت 09xxxxxxxxx باشه',
)


class Resident(BaseModel):
    """
    هویت یک ساکن/مالک به‌عنوان شخص — مستقل از حساب کاربری (User).
    چرا جدا از User؟ چون خیلی از ساکنین (مثلاً همسر، فرزند، مالک غیرمقیم)
    ممکنه هیچ‌وقت وارد سیستم نشن و لاگین نداشته باشن، ولی باید در قبض/تماس
    اضطراری/لیست ساکنین ثبت باشن. اگه واقعاً حساب کاربری داشته باشه،
    از طریق فیلد user وصل می‌شه.
    """
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_profile',
        verbose_name='حساب کاربری (اختیاری)',
        help_text='فقط اگه این شخص قراره وارد پنل بشه پر کن',
    )
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    phone_number = models.CharField(
        max_length=11, validators=[phone_validator], verbose_name='شماره موبایل'
    )
    national_code = models.CharField(
        max_length=10, blank=True, null=True, verbose_name='کد ملی'
    )
    emergency_contact_name = models.CharField(
        max_length=150, blank=True, verbose_name='نام تماس اضطراری'
    )
    emergency_contact_phone = models.CharField(
        max_length=11, blank=True, verbose_name='شماره تماس اضطراری'
    )

    class Meta:
        verbose_name = 'ساکن'
        verbose_name_plural = 'ساکنین'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UnitResident(BaseModel):
    """
    رابطه‌ی واسط بین Resident و Unit — یک ساکن می‌تونه در طول زمان
    در چند واحد (یا چند دوره‌ی زمانی از یک واحد) نقش داشته باشه،
    برای همین این رابطه تاریخ‌دار و نوع‌دار تعریف شده، نه FK مستقیم.
    """
    class ResidencyType(models.TextChoices):
        OWNER = 'owner', 'مالک'
        TENANT = 'tenant', 'مستاجر'

    resident = models.ForeignKey(
        Resident, on_delete=models.CASCADE,
        related_name='unit_residencies', verbose_name='ساکن'
    )
    unit = models.ForeignKey(
        'buildings.Unit', on_delete=models.CASCADE,
        related_name='residencies', verbose_name='واحد'
    )
    residency_type = models.CharField(
        max_length=10, choices=ResidencyType.choices, verbose_name='نوع رابطه'
    )
    is_primary_contact = models.BooleanField(
        default=False, verbose_name='مخاطب اصلی واحد',
        help_text='برای قبض/اعلانیه به این شخص اولویت داده می‌شه',
    )
    start_date = models.DateField(verbose_name='تاریخ شروع سکونت/مالکیت')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پایان (اگه تموم‌شده)')
    is_current = models.BooleanField(default=True, verbose_name='رابطه‌ی فعال')

    class Meta:
        verbose_name = 'ساکن-واحد'
        verbose_name_plural = 'ساکنین-واحدها'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.resident} - {self.unit} ({self.get_residency_type_display()})"