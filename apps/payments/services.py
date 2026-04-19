from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.common.models import InstallmentStatus, PaymentFrequency, quantize_money
from apps.payments.models import LeaseInstallment, Payment, PaymentAllocation


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def due_date_for_period(period_start, due_day):
    return period_start.replace(day=min(due_day, monthrange(period_start.year, period_start.month)[1]))


def recalculate_installment(installment):
    total_due = quantize_money(installment.amount_due + installment.late_fee_amount + installment.adjustment_amount)
    amount_paid = installment.allocations.aggregate(total=Sum("allocated_amount")).get("total") or Decimal("0.00")
    installment.amount_paid = quantize_money(amount_paid)
    installment.outstanding_amount = quantize_money(total_due - installment.amount_paid)

    if installment.outstanding_amount <= 0:
        installment.status = InstallmentStatus.PAID
        installment.outstanding_amount = Decimal("0.00")
    elif installment.amount_paid > 0:
        installment.status = InstallmentStatus.PARTIAL
    else:
        installment.status = InstallmentStatus.UNPAID

    grace_cutoff = installment.due_date + timedelta(days=installment.lease.grace_days)
    if installment.outstanding_amount > 0 and timezone.localdate() > grace_cutoff:
        installment.status = InstallmentStatus.OVERDUE

    installment.save(update_fields=["amount_paid", "outstanding_amount", "status", "updated_at"])
    return installment


@transaction.atomic
def generate_payment_schedule(lease):
    if lease.installments.exists():
        return lease.installments.all()

    step = 1 if lease.payment_frequency == PaymentFrequency.MONTHLY else 3
    period_start = lease.start_date
    installments = []
    while period_start < lease.end_date:
        next_start = add_months(period_start, step)
        period_end = min(next_start, lease.end_date)
        installment = LeaseInstallment.objects.create(
            landlord=lease.landlord,
            lease=lease,
            billing_period_start=period_start,
            billing_period_end=period_end,
            due_date=due_date_for_period(period_start, lease.due_day),
            amount_due=lease.rent_amount,
            outstanding_amount=lease.rent_amount,
        )
        installments.append(installment)
        period_start = next_start
    return installments


@transaction.atomic
def allocate_payment(payment, installments=None):
    remaining = quantize_money(payment.amount)
    installments = installments or LeaseInstallment.objects.select_for_update().filter(
        lease=payment.lease,
        landlord=payment.landlord,
    ).exclude(status=InstallmentStatus.PAID).order_by("due_date", "billing_period_start")

    for installment in installments:
        if remaining <= 0:
            break
        allocatable = min(remaining, installment.outstanding_amount)
        if allocatable <= 0:
            continue
        PaymentAllocation.objects.create(payment=payment, installment=installment, allocated_amount=allocatable)
        recalculate_installment(installment)
        remaining = quantize_money(remaining - allocatable)
    return payment


@transaction.atomic
def record_payment(*, landlord, created_by, **data):
    lease = data["lease"]
    tenant = data["tenant"]
    if lease.landlord_id != landlord.id or tenant.landlord_id != landlord.id:
        raise ValidationError("Lease and tenant must belong to the current landlord.")
    if tenant.id != lease.tenant_id:
        raise ValidationError("The selected tenant must match the lease tenant.")

    payment = Payment.objects.create(landlord=landlord, created_by=created_by, **data)
    allocate_payment(payment)
    return payment


def refresh_overdue_statuses(landlord):
    for installment in LeaseInstallment.objects.filter(landlord=landlord).select_related("lease"):
        recalculate_installment(installment)
