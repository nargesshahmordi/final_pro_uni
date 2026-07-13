from django.core.validators import MinValueValidator
from django.db import models

from apps.audit.registry import audit_model
from apps.common.models import BaseModel


@audit_model(building_field='building')
class ChargeRule(BaseModel):
    """
    نسخه‌ای از فرمول شارژ یک ساختمان: total = fixed_amount + area * rate_per_area

    قانون پروژه: هرگز overwrite نشه. برای تغییر نرخ، رکورد قبلی effective_to
    می‌گیره (توسط services.charge_calculation.create_new_charge_rule_version)
    و رکورد جدید effective_from همون تاریخ ساخته می‌شه. این‌جوری صدور مجدد
    قبض‌های گذشته همیشه با نرخ همون‌زمان محاسبه می‌شه.
    """
    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='charge_rules', verbose_name='ساختمان'
    )
    title = models.CharField(max_length=150, blank=True, verbose_name='عنوان')
    fixed_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ ثابت (ریال)',
    )
    rate_per_area = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        validators=[MinValueValidator(0)],
        verbose_name='نرخ به ازای هر متر مربع (ریال)',
    )
    effective_from = models.DateField(verbose_name='اعتبار از تاریخ')
    effective_to = models.DateField(
        null=True, blank=True,
        verbose_name='اعتبار تا تاریخ',
        help_text='خالی = تا اطلاع ثانوی (نسخه‌ی جاری)',
    )
    notes = models.TextField(blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'قانون شارژ'
        verbose_name_plural = 'قوانین شارژ (نسخه‌دار)'
        ordering = ['-effective_from']
        indexes = [models.Index(fields=['building', 'effective_from'])]

    def __str__(self):
        to = self.effective_to.isoformat() if self.effective_to else 'جاری'
        return f"{self.building.name} - از {self.effective_from} تا {to}"


@audit_model(building_field='building')
class Invoice(BaseModel):
    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'پرداخت‌نشده'
        PARTIAL = 'partial', 'پرداخت‌جزئی'
        PAID = 'paid', 'پرداخت‌شده'
        OVERDUE = 'overdue', 'معوق'
        CANCELLED = 'cancelled', 'لغوشده'

    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='invoices', verbose_name='ساختمان'
    )
    unit = models.ForeignKey(
        'buildings.Unit', on_delete=models.CASCADE,
        related_name='invoices', verbose_name='واحد'
    )
    charge_rule = models.ForeignKey(
        ChargeRule, on_delete=models.PROTECT,
        related_name='invoices', verbose_name='قانون شارژ اعمال‌شده',
        help_text='PROTECT عمدیه — نباید بشه rule ای که قبض بهش وصله رو حذف کرد',
    )
    period = models.DateField(
        verbose_name='دوره (روز اول ماه)',
        help_text='برای یکنواختی همیشه روز اول ماه ذخیره می‌شه',
    )
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='مبلغ ثابت')
    area_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='مبلغ متراژی')
    extra_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        verbose_name='مبلغ اضافی موردی',
        help_text='هزینه‌ی موردی/جریمه/تعدیل که جزو فرمول ثابت شارژ نیست',
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='مبلغ کل')
    due_date = models.DateField(verbose_name='سررسید')
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.UNPAID, verbose_name='وضعیت'
    )
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان صدور')

    class Meta:
        verbose_name = 'قبض'
        verbose_name_plural = 'قبض‌ها'
        unique_together = ('unit', 'period')
        ordering = ['-period']
        indexes = [models.Index(fields=['unit', '-period']), models.Index(fields=['status'])]

    def __str__(self):
        return f"قبض {self.unit} - {self.period:%Y-%m}"


@audit_model(building_field='building')
class Payment(BaseModel):
    class Method(models.TextChoices):
        CASH = 'cash', 'نقدی'
        CARD = 'card', 'کارت‌به‌کارت'
        GATEWAY = 'gateway', 'درگاه پرداخت'
        CHEQUE = 'cheque', 'چک'

    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار تایید'
        CONFIRMED = 'confirmed', 'تاییدشده'
        FAILED = 'failed', 'ناموفق'
        REFUNDED = 'refunded', 'بازگشت‌داده‌شده'

    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='payments', verbose_name='ساختمان'
    )
    unit = models.ForeignKey(
        'buildings.Unit', on_delete=models.CASCADE,
        related_name='payments', verbose_name='واحد'
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='payments', verbose_name='قبض مرتبط',
        help_text='اگه پیش‌پرداخت/بدون قبض مشخص باشه خالی بذار',
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ',
    )
    method = models.CharField(max_length=10, choices=Method.choices, verbose_name='روش پرداخت')
    reference_code = models.CharField(max_length=100, blank=True, verbose_name='کد پیگیری')
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name='وضعیت'
    )
    paid_at = models.DateTimeField(verbose_name='زمان پرداخت')
    confirmed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='confirmed_payments', verbose_name='تاییدکننده',
        help_text='معمولاً برای پرداخت نقدی/کارت‌به‌کارت که نیاز به تایید مدیر داره',
    )

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-paid_at']
        indexes = [models.Index(fields=['unit', '-paid_at'])]

    def __str__(self):
        return f"پرداخت {self.amount} - {self.unit} - {self.get_status_display()}"


@audit_model(building_field='building')
class Transaction(BaseModel):
    """
    دفتر حساب (ledger) هر واحد — append-only، هرگز ویرایش/حذف نمی‌شه.
    منبع واحد حقیقت برای «بدهی من» به‌جای جمع‌زدن زنده‌ی invoice/payment هر بار.
    """
    class Kind(models.TextChoices):
        CHARGE = 'charge', 'شارژ (بدهکار)'
        PAYMENT = 'payment', 'پرداخت (بستانکار)'
        ADJUSTMENT = 'adjustment', 'تعدیل بدهکار'
        REFUND = 'refund', 'بازگشت وجه (بستانکار)'

    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='transactions', verbose_name='ساختمان'
    )
    unit = models.ForeignKey(
        'buildings.Unit', on_delete=models.CASCADE,
        related_name='transactions', verbose_name='واحد'
    )
    kind = models.CharField(max_length=12, choices=Kind.choices, verbose_name='نوع تراکنش')
    amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        verbose_name='مبلغ (امضادار)',
        help_text='مثبت = افزایش بدهی واحد، منفی = کاهش بدهی (پرداخت/بازگشت)',
    )
    balance_after = models.DecimalField(
        max_digits=12, decimal_places=0,
        verbose_name='مانده بعد از این تراکنش',
    )
    related_invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions', verbose_name='قبض مرتبط'
    )
    related_payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions', verbose_name='پرداخت مرتبط'
    )
    description = models.CharField(max_length=255, blank=True, verbose_name='شرح')

    class Meta:
        verbose_name = 'تراکنش دفتر حساب'
        verbose_name_plural = 'تراکنش‌های دفتر حساب'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['unit', '-created_at'])]

    def __str__(self):
        return f"{self.get_kind_display()} {self.amount} - {self.unit}"


@audit_model(building_field='building')
class Expense(BaseModel):
    """
    هزینه‌ی سطح ساختمان (نه واحد) — حقوق سرایدار، تعمیرات مشاعات و... .
    جدا از Invoice/Transaction چون به حساب هیچ واحد خاصی وصل نیست؛
    برای گزارش «هزینه‌ها در برابر شارژهای وصولی» استفاده می‌شه.
    """
    class Category(models.TextChoices):
        STAFF_SALARY = 'staff_salary', 'حقوق سرایدار/کارمند'
        REPAIR = 'repair', 'تعمیرات'
        UTILITIES = 'utilities', 'تاسیسات (آب/برق/گاز مشاعات)'
        CLEANING = 'cleaning', 'نظافت'
        INSURANCE = 'insurance', 'بیمه'
        OTHER = 'other', 'سایر'

    building = models.ForeignKey(
        'buildings.Building', on_delete=models.CASCADE,
        related_name='expenses', verbose_name='ساختمان'
    )
    category = models.CharField(max_length=20, choices=Category.choices, verbose_name='دسته‌بندی')
    title = models.CharField(max_length=255, verbose_name='عنوان')
    amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ',
    )
    expense_date = models.DateField(verbose_name='تاریخ هزینه')
    paid_to = models.CharField(max_length=255, blank=True, verbose_name='پرداخت به')
    receipt = models.FileField(
        upload_to='expense_receipts/%Y/%m/', null=True, blank=True, verbose_name='رسید'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'هزینه'
        verbose_name_plural = 'هزینه‌ها'
        ordering = ['-expense_date']
        indexes = [models.Index(fields=['building', '-expense_date'])]

    def __str__(self):
        return f"{self.title} - {self.amount} - {self.building.name}"
