from django.db import models
from django.urls import reverse

from apps.common.models import ExpenseCategory, LandlordOwnedModel, PaymentMethod, TimeStampedModel


class Expense(TimeStampedModel, LandlordOwnedModel):
    property = models.ForeignKey("properties.Property", on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses")
    expense_date = models.DateField()
    category = models.CharField(max_length=30, choices=ExpenseCategory.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    vendor_name = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to="expense_attachments/", blank=True)

    class Meta:
        ordering = ["-expense_date", "-created_at"]
        indexes = [models.Index(fields=["landlord", "expense_date"])]

    def __str__(self):
        return f"{self.category} / {self.amount}"

    def get_absolute_url(self):
        return reverse("expenses:list")
