from decimal import Decimal

from django.apps import apps
from django.db.models import Sum

from apps.common.models import LeaseStatus
from apps.tenants.models import Tenant


def tenant_queryset_for_landlord(landlord):
    return Tenant.objects.filter(landlord=landlord)


def tenant_detail_context(tenant):
    """Leases, payment history, and balances for a single tenant."""
    Lease = apps.get_model("leases", "Lease")
    Payment = apps.get_model("payments", "Payment")
    LeaseInstallment = apps.get_model("payments", "LeaseInstallment")

    leases = list(
        Lease.objects.filter(tenant=tenant).select_related("property").order_by("-start_date")
    )
    active_leases = [lease for lease in leases if lease.status == LeaseStatus.ACTIVE]

    total_paid = Payment.objects.filter(tenant=tenant).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    outstanding = LeaseInstallment.objects.filter(
        lease__tenant=tenant
    ).aggregate(total=Sum("outstanding_amount"))["total"] or Decimal("0")

    payments = list(
        Payment.objects.filter(tenant=tenant)
        .select_related("lease", "lease__property")
        .order_by("-payment_date")[:8]
    )

    return {
        "leases": leases,
        "lease_count": len(leases),
        "active_lease_count": len(active_leases),
        "total_paid": total_paid,
        "outstanding_amount": outstanding,
        "payments": payments,
    }
