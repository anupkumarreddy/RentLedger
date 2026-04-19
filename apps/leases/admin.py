from django.contrib import admin

from apps.leases.models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ("property", "tenant", "landlord", "rent_amount", "status", "start_date", "end_date")
    list_filter = ("status", "payment_frequency")
