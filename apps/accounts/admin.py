from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, BuildingMembership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('phone_number',)
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name', 'national_code')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات فردی', {'fields': ('first_name', 'last_name', 'email', 'national_code', 'avatar')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
    
@admin.register(BuildingMembership)
class BuildingMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'building', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'building')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
