from django.contrib import admin

from .models import ChargeRule, Invoice, Payment, Transaction, Expense


@admin.register(ChargeRule)
class ChargeRuleAdmin(admin.ModelAdmin):
    list_display = ('building', 'fixed_amount', 'rate_per_area', 'effective_from', 'effective_to')
    list_filter = ('building',)
    # عمداً هیچ inline/فرم سریعی برای ساخت نسخه‌ی جدید اینجا نیست؛
    # ساخت نسخه‌ی جدید باید از services.charge_calculation.create_new_charge_rule_version
    # انجام بشه تا effective_to نسخه‌ی قبلی درست بسته بشه.


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ('kind', 'amount', 'balance_after', 'description', 'created_at')
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('unit', 'period', 'total_amount', 'status', 'due_date')
    list_filter = ('status', 'building', 'period')
    search_fields = ('unit__unit_number',)
    readonly_fields = ('fixed_amount', 'area_amount', 'total_amount', 'charge_rule', 'issued_at')
    inlines = [TransactionInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('unit', 'amount', 'method', 'status', 'paid_at', 'confirmed_by')
    list_filter = ('status', 'method', 'building')
    search_fields = ('unit__unit_number', 'reference_code')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('unit', 'kind', 'amount', 'balance_after', 'created_at')
    list_filter = ('kind', 'building')
    search_fields = ('unit__unit_number',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'building', 'category', 'amount', 'expense_date')
    list_filter = ('category', 'building')
    search_fields = ('title', 'paid_to')
