from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only عمدی: audit log نباید از پنل ادمین قابل ویرایش یا حذف باشه،
    وگرنه کل هدف audit (بدون‌ردپا نبودن تغییرات حساس) زیر سوال می‌ره.
    """
    list_display = ('created_at', 'actor', 'action', 'content_type', 'object_repr', 'building')
    list_filter = ('action', 'content_type', 'building')
    search_fields = ('object_repr', 'actor__phone_number')
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
