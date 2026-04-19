from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.common.models import InstallmentStatus, LeaseStatus
from apps.expenses.models import Expense
from apps.leases.models import Lease
from apps.payments.models import LeaseInstallment, Payment
from apps.properties.models import Property


def dashboard_snapshot(landlord):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    next_30 = today + timedelta(days=30)

    property_count = Property.objects.filter(landlord=landlord, is_active=True).count()
    occupied_units = Property.objects.filter(landlord=landlord, leases__status=LeaseStatus.ACTIVE).distinct().count()
    active_leases = Lease.objects.filter(landlord=landlord, status=LeaseStatus.ACTIVE)
    rent_due = LeaseInstallment.objects.filter(landlord=landlord, due_date__range=(month_start, today)).aggregate(total=Sum("amount_due"))["total"] or 0
    collected = Payment.objects.filter(landlord=landlord, payment_date__range=(month_start, today)).aggregate(total=Sum("amount"))["total"] or 0
    overdue_amount = sum(i.outstanding_amount for i in LeaseInstallment.objects.filter(landlord=landlord) if i.is_overdue_now)
    expenses_total = Expense.objects.filter(landlord=landlord, expense_date__range=(month_start, today)).aggregate(total=Sum("amount"))["total"] or 0

    return {
        "total_properties": property_count,
        "occupied_units": occupied_units,
        "vacant_units": max(property_count - occupied_units, 0),
        "active_leases": active_leases.count(),
        "monthly_expected_rent": rent_due,
        "monthly_collected_rent": collected,
        "overdue_amount": overdue_amount,
        "expenses_this_month": expenses_total,
        "net_cash_flow": collected - expenses_total,
        "upcoming_expirations": active_leases.filter(end_date__lte=next_30).select_related("property", "tenant")[:5],
        "recent_payments": Payment.objects.filter(landlord=landlord).select_related("lease", "tenant", "lease__property")[:5],
        "recent_expenses": Expense.objects.filter(landlord=landlord).select_related("property")[:5],
        "upcoming_dues": LeaseInstallment.objects.filter(landlord=landlord, due_date__gte=today).select_related("lease", "lease__property", "lease__tenant")[:5],
        "overdue_installments": [i for i in LeaseInstallment.objects.filter(landlord=landlord).select_related("lease", "lease__property", "lease__tenant") if i.is_overdue_now][:5],
    }
