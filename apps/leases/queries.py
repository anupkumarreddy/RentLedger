from decimal import Decimal

from django.apps import apps
from django.db.models import Sum

from apps.common.models import LeaseStatus


def lease_queryset_for_landlord(landlord):
    Lease = apps.get_model("leases", "Lease")
    return Lease.objects.filter(landlord=landlord).select_related("property", "tenant")


def lease_detail_context(lease):
    """Installment rollups and payment history for a lease."""
    Payment = apps.get_model("payments", "Payment")

    installments = list(lease.installments.all())
    total_billed = sum(
        (i.amount_due + i.late_fee_amount + i.adjustment_amount for i in installments),
        Decimal("0"),
    )
    total_paid = sum((i.amount_paid for i in installments), Decimal("0"))
    total_outstanding = sum((i.outstanding_amount for i in installments), Decimal("0"))

    payments = list(
        Payment.objects.filter(lease=lease).order_by("-payment_date", "-created_at")[:10]
    )

    return {
        "installments": installments,
        "installment_count": len(installments),
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
        "lease_payments": payments,
    }


def active_leases_for_property(property_obj, *, exclude_lease_id=None):
    Lease = apps.get_model("leases", "Lease")
    queryset = Lease.objects.filter(property=property_obj, status=LeaseStatus.ACTIVE)
    if exclude_lease_id:
        queryset = queryset.exclude(pk=exclude_lease_id)
    return queryset
