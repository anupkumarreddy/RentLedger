from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.common.models import CreatedByMixin, InstallmentStatus, LandlordOwnedModel, PaymentMethod, TimeStampedModel


class LeaseInstallment(TimeStampedModel, LandlordOwnedModel):
    lease = models.ForeignKey("leases.Lease", on_delete=models.CASCADE, related_name="installments")
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    late_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjustment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=InstallmentStatus.choices, default=InstallmentStatus.UNPAID)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["due_date"]
        indexes = [models.Index(fields=["landlord", "status", "due_date"])]

    def __str__(self):
        return f"{self.lease} / {self.billing_period_start}"

    def get_absolute_url(self):
        return reverse("payments:installment_detail", args=[self.pk])

    @property
    def is_overdue_now(self):
        due_date = self.due_date
        grace_days = getattr(self.lease, "grace_days", 0) or 0
        grace_cutoff = due_date + timedelta(days=int(grace_days))
        return self.outstanding_amount > 0 and timezone.localdate() > grace_cutoff


class Payment(TimeStampedModel, LandlordOwnedModel, CreatedByMixin):
    lease = models.ForeignKey("leases.Lease", on_delete=models.PROTECT, related_name="payments")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="payments")
    payment_date = models.DateField(default=timezone.localdate)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER)
    reference_number = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    audit_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        indexes = [models.Index(fields=["landlord", "payment_date"])]

    def __str__(self):
        return f"Payment {self.amount} on {self.payment_date}"


class PaymentAllocation(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="allocations")
    installment = models.ForeignKey(LeaseInstallment, on_delete=models.CASCADE, related_name="allocations")
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["installment__due_date"]

    def __str__(self):
        return f"{self.payment} -> {self.installment}"
