from django.contrib import admin

from apps.payments.models import LeaseInstallment, Payment, PaymentAllocation


admin.site.register(LeaseInstallment)
admin.site.register(Payment)
admin.site.register(PaymentAllocation)
