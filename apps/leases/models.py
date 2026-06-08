from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from apps.common.models import LateFeeType, LeaseStatus, LandlordOwnedModel, PaymentFrequency, TimeStampedModel


class Lease(TimeStampedModel, LandlordOwnedModel):
    property = models.ForeignKey("properties.Property", on_delete=models.PROTECT, related_name="leases")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="leases")
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    security_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    payment_frequency = models.CharField(max_length=20, choices=PaymentFrequency.choices, default=PaymentFrequency.MONTHLY)
    due_day = models.PositiveSmallIntegerField(default=5)
    grace_days = models.PositiveSmallIntegerField(default=0)
    late_fee_type = models.CharField(max_length=20, choices=LateFeeType.choices, default=LateFeeType.NONE)
    late_fee_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    status = models.CharField(max_length=20, choices=LeaseStatus.choices, default=LeaseStatus.DRAFT)
    lease_document = models.FileField(upload_to="lease_documents/", blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["landlord", "status"]),
            models.Index(fields=["property", "start_date", "end_date"]),
            models.Index(fields=["tenant", "status"]),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(rent_amount__gte=0), name="leases_rent_amount_non_negative"),
            models.CheckConstraint(condition=Q(security_deposit__gte=0), name="leases_security_deposit_non_negative"),
            models.CheckConstraint(condition=Q(late_fee_value__gte=0), name="leases_late_fee_value_non_negative"),
        ]

    def __str__(self):
        return f"{self.property} - {self.tenant}"

    def get_absolute_url(self):
        return reverse("leases:detail", args=[self.pk])

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("Lease end date must be after the start date.")
        if self.due_day < 1 or self.due_day > 28:
            raise ValidationError("Due day must be between 1 and 28 for schedule generation.")
