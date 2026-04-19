from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IsActiveMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class LandlordOwnedModel(models.Model):
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True


class CreatedByMixin(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )

    class Meta:
        abstract = True


class PropertyType(models.TextChoices):
    APARTMENT = "apartment", "Apartment"
    VILLA = "villa", "Villa"
    COMMERCIAL = "commercial", "Commercial"
    PLOT = "plot", "Plot"
    ROOM = "room", "Room"


class PaymentFrequency(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"


class LeaseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    TERMINATED = "terminated", "Terminated"
    CANCELLED = "cancelled", "Cancelled"


class LateFeeType(models.TextChoices):
    NONE = "none", "None"
    FIXED = "fixed", "Fixed"
    PERCENTAGE = "percentage", "Percentage"


class InstallmentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PARTIAL = "partial", "Partial"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    UPI = "upi", "UPI"
    CHEQUE = "cheque", "Cheque"
    OTHER = "other", "Other"


class ExpenseCategory(models.TextChoices):
    MAINTENANCE = "maintenance", "Maintenance"
    REPAIR = "repair", "Repair"
    TAX = "tax", "Tax"
    UTILITY = "utility", "Utility"
    INSURANCE = "insurance", "Insurance"
    SOCIETY_FEE = "society_fee", "Society Fee"
    BROKER_FEE = "broker_fee", "Broker Fee"
    OTHER = "other", "Other"


MONEY_PLACES = Decimal("0.01")


def quantize_money(value):
    return Decimal(value).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
