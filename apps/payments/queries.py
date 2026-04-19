from django.db.models import Sum

from apps.common.models import InstallmentStatus, LeaseStatus
from apps.payments.models import LeaseInstallment, Payment


def due_installments_for_landlord(landlord):
    return LeaseInstallment.objects.filter(landlord=landlord).select_related("lease", "lease__property", "lease__tenant")


def overdue_installments_for_landlord(landlord):
    return due_installments_for_landlord(landlord).filter(status=InstallmentStatus.OVERDUE)


def payments_for_landlord(landlord):
    return Payment.objects.filter(landlord=landlord).select_related("lease", "tenant")


def monthly_collected_amount(landlord, start_date, end_date):
    return payments_for_landlord(landlord).filter(payment_date__range=(start_date, end_date)).aggregate(total=Sum("amount"))["total"] or 0
