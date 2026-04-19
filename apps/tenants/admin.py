from django.contrib import admin

from apps.tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "landlord", "phone", "email", "is_active")
    search_fields = ("full_name", "email", "phone")
