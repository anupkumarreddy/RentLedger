from django.contrib import admin

from apps.properties.models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "landlord", "property_type", "city", "is_active")
    search_fields = ("name", "city", "state")
