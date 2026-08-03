from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.common.models import LeaseStatus
from apps.expenses.models import Expense
from apps.leases.models import Lease
from apps.payments.models import LeaseInstallment, Payment
from apps.properties.models import Property


def _month_bounds(day):
    start = day.replace(day=1)
    end = day.replace(day=monthrange(day.year, day.month)[1])
    return start, end


def _shift_month(day, months):
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def monthly_series(landlord, today, months=6):
    """Collected rent vs expenses for each of the last ``months`` months."""
    series = []
    first = _shift_month(today, -(months - 1))
    cursor = first
    while cursor <= today:
        start, end = _month_bounds(cursor)
        collected = Payment.objects.filter(
            landlord=landlord, payment_date__range=(start, end)
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        expenses = Expense.objects.filter(
            landlord=landlord, expense_date__range=(start, end)
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        series.append(
            {
                "label": cursor.strftime("%b"),
                "collected": collected,
                "expenses": expenses,
            }
        )
        cursor = _shift_month(cursor, 1)
    return series


def dashboard_snapshot(landlord):
    today = timezone.localdate()
    month_start, month_end = _month_bounds(today)
    next_30 = today + timedelta(days=30)

    property_count = Property.objects.filter(landlord=landlord, is_active=True).count()
    occupied_units = (
        Property.objects.filter(landlord=landlord, leases__status=LeaseStatus.ACTIVE)
        .distinct()
        .count()
    )
    active_leases = Lease.objects.filter(landlord=landlord, status=LeaseStatus.ACTIVE)

    # Expected rent = installments billed for the current month.
    expected = LeaseInstallment.objects.filter(
        landlord=landlord, due_date__range=(month_start, month_end)
    ).aggregate(total=Sum("amount_due"))["total"] or Decimal("0")
    collected = Payment.objects.filter(
        landlord=landlord, payment_date__range=(month_start, month_end)
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    expenses_total = Expense.objects.filter(
        landlord=landlord, expense_date__range=(month_start, month_end)
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    overdue_qs = [
        i
        for i in LeaseInstallment.objects.filter(landlord=landlord).select_related(
            "lease", "lease__property", "lease__tenant"
        )
        if i.is_overdue_now
    ]
    overdue_amount = sum((i.outstanding_amount for i in overdue_qs), Decimal("0"))

    occupancy_rate = round(occupied_units / property_count * 100) if property_count else 0
    collection_rate = (
        round(min(collected, expected) / expected * 100) if expected else 0
    )

    series = monthly_series(landlord, today)
    series_max = max(
        [max(m["collected"], m["expenses"]) for m in series] + [Decimal("1")]
    )

    return {
        "total_properties": property_count,
        "occupied_units": occupied_units,
        "vacant_units": max(property_count - occupied_units, 0),
        "occupancy_rate": occupancy_rate,
        "active_leases": active_leases.count(),
        "monthly_expected_rent": expected,
        "monthly_collected_rent": collected,
        "collection_rate": collection_rate,
        "overdue_amount": overdue_amount,
        "overdue_count": len(overdue_qs),
        "expenses_this_month": expenses_total,
        "net_cash_flow": collected - expenses_total,
        "trend_series": series,
        "trend_max": series_max,
        "upcoming_expirations": active_leases.filter(end_date__lte=next_30)
        .filter(end_date__gte=today)
        .select_related("property", "tenant")[:5],
        "recent_payments": Payment.objects.filter(landlord=landlord).select_related(
            "lease", "tenant", "lease__property"
        )[:5],
        "upcoming_dues": LeaseInstallment.objects.filter(
            landlord=landlord, due_date__gte=today
        )
        .exclude(status="paid")
        .select_related("lease", "lease__property", "lease__tenant")[:5],
        "overdue_installments": overdue_qs[:5],
    }
