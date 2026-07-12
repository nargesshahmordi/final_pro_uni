from django.contrib import admin

from .models import Building, Block, Unit, Parking, Storage


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'total_floors', 'construction_year')
    search_fields = ('name', 'city', 'address')
    inlines = [BlockInline]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    list_filter = ('building',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'building', 'block', 'floor', 'area', 'unit_type')
    list_filter = ('building', 'unit_type')
    search_fields = ('unit_number',)


@admin.register(Parking)
class ParkingAdmin(admin.ModelAdmin):
    list_display = ('number', 'building', 'unit')
    list_filter = ('building',)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('number', 'building', 'unit')
    list_filter = ('building',)