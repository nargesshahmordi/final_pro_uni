from django.contrib import admin

from .models import Resident, UnitResident


class UnitResidentInline(admin.TabularInline):
    model = UnitResident
    extra = 0
    fields = ('unit', 'residency_type', 'is_primary_contact', 'start_date', 'end_date', 'is_current')


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'user')
    search_fields = ('first_name', 'last_name', 'phone_number', 'national_code')
    inlines = [UnitResidentInline]


@admin.register(UnitResident)
class UnitResidentAdmin(admin.ModelAdmin):
    list_display = ('resident', 'unit', 'residency_type', 'is_current', 'is_primary_contact', 'start_date')
    list_filter = ('residency_type', 'is_current', 'unit__building')
    search_fields = ('resident__first_name', 'resident__last_name', 'unit__unit_number')