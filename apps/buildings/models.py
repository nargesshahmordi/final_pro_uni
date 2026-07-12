from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class Building(BaseModel):
    name = models.CharField(max_length=255, verbose_name='نام ساختمان')
    province = models.CharField(max_length=100, verbose_name='استان')
    city = models.CharField(max_length=100, verbose_name='شهر')
    address = models.TextField(verbose_name='آدرس')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='کد پستی')
    total_floors = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد طبقات')
    construction_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='سال ساخت')

    class Meta:
        verbose_name = 'ساختمان'
        verbose_name_plural = 'ساختمان‌ها'

    def __str__(self):
        return self.name


class Block(BaseModel):
    """
    بلوک اختیاریه — ساختمان‌های کوچیک ممکنه اصلاً بلوک نداشته باشن،
    برای همین Unit مستقیم هم به Building وصله هم (اختیاری) به Block.
    """
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='blocks', verbose_name='ساختمان'
    )
    name = models.CharField(max_length=50, verbose_name='نام/شماره بلوک')

    class Meta:
        unique_together = ('building', 'name')
        verbose_name = 'بلوک'
        verbose_name_plural = 'بلوک‌ها'

    def __str__(self):
        return f"{self.building.name} - بلوک {self.name}"


class Unit(BaseModel):
    class UnitType(models.TextChoices):
        RESIDENTIAL = 'residential', 'مسکونی'
        COMMERCIAL = 'commercial', 'تجاری'
        OFFICE = 'office', 'اداری'

    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='units', verbose_name='ساختمان'
    )
    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name='units',
        null=True, blank=True, verbose_name='بلوک'
    )
    unit_number = models.CharField(max_length=20, verbose_name='شماره واحد')
    floor = models.SmallIntegerField(verbose_name='طبقه')
    area = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='متراژ (متر مربع)',
        help_text='برای فرمول شارژ (fixed + area × rate) استفاده می‌شه',
    )
    unit_type = models.CharField(
        max_length=20, choices=UnitType.choices, default=UnitType.RESIDENTIAL, verbose_name='نوع واحد'
    )
    bedroom_count = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد خواب')

    class Meta:
        unique_together = ('building', 'unit_number')
        verbose_name = 'واحد'
        verbose_name_plural = 'واحدها'

    def __str__(self):
        return f"واحد {self.unit_number} - {self.building.name}"


class Parking(BaseModel):
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='parkings', verbose_name='ساختمان'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='parkings', verbose_name='واحد متصل‌شده',
        help_text='اگه پارکینگ مشترک/بدون تخصیص باشه خالی بذار',
    )
    number = models.CharField(max_length=20, verbose_name='شماره پارکینگ')

    class Meta:
        unique_together = ('building', 'number')
        verbose_name = 'پارکینگ'
        verbose_name_plural = 'پارکینگ‌ها'

    def __str__(self):
        return f"پارکینگ {self.number} - {self.building.name}"


class Storage(BaseModel):
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='storages', verbose_name='ساختمان'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='storages', verbose_name='واحد متصل‌شده'
    )
    number = models.CharField(max_length=20, verbose_name='شماره انباری')

    class Meta:
        unique_together = ('building', 'number')
        verbose_name = 'انباری'
        verbose_name_plural = 'انباری‌ها'

    def __str__(self):
        return f"انباری {self.number} - {self.building.name}"