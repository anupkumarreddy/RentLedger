from decimal import Decimal

from django.apps import apps
from django.db.models import Exists, OuterRef, Sum
from django.utils import timezone

from apps.common.models import LeaseStatus
from apps.properties.models import Property


def property_queryset_for_landlord(landlord):
    Lease = apps.get_model("leases", "Lease")
    active_lease = Lease.objects.filter(
        landlord=landlord,
        property=OuterRef("pk"),
        status=LeaseStatus.ACTIVE,
    )
    return Property.objects.filter(landlord=landlord).annotate(is_occupied=Exists(active_lease))


def property_detail_context(property_obj):
    """Related leases, occupancy, and financial rollups for a property."""
    Lease = apps.get_model("leases", "Lease")
    Expense = apps.get_model("expenses", "Expense")
    LeaseInstallment = apps.get_model("payments", "LeaseInstallment")

    leases = list(
        Lease.objects.filter(property=property_obj)
        .select_related("tenant")
        .order_by("-start_date")
    )
    active_lease = next((lease for lease in leases if lease.status == LeaseStatus.ACTIVE), None)

    year_start = timezone.localdate().replace(month=1, day=1)
    ytd_expenses = Expense.objects.filter(
        property=property_obj, expense_date__gte=year_start
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    outstanding = LeaseInstallment.objects.filter(
        lease__property=property_obj
    ).aggregate(total=Sum("outstanding_amount"))["total"] or Decimal("0")

    recent_expenses = list(
        Expense.objects.filter(property=property_obj).order_by("-expense_date")[:5]
    )

    return {
        "active_lease": active_lease,
        "leases": leases,
        "lease_count": len(leases),
        "monthly_rent": active_lease.rent_amount if active_lease else property_obj.rent_default,
        "ytd_expenses": ytd_expenses,
        "outstanding_amount": outstanding,
        "recent_expenses": recent_expenses,
    }
