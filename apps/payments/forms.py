from decimal import Decimal

from django import forms
from django.utils import timezone

from apps.common.forms import BaseStyledForm, DateInput
from apps.common.models import PaymentMethod
from apps.payments.models import Payment


class PaymentForm(BaseStyledForm):
    class Meta:
        model = Payment
        fields = ["lease", "tenant", "payment_date", "amount", "payment_method", "reference_number", "notes", "audit_note"]
        widgets = {"payment_date": DateInput()}

    def __init__(self, *args, landlord=None, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord is not None:
            self.fields["lease"].queryset = self.fields["lease"].queryset.filter(landlord=landlord)
            self.fields["tenant"].queryset = self.fields["tenant"].queryset.filter(landlord=landlord)


class InstallmentPaymentForm(forms.Form):
    """Record a full or partial payment against a single installment."""

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Defaults to the full outstanding balance. Lower it for a partial payment.",
    )
    payment_date = forms.DateField(widget=DateInput(), initial=timezone.localdate)
    payment_method = forms.ChoiceField(choices=PaymentMethod.choices, initial=PaymentMethod.BANK_TRANSFER)
    reference_number = forms.CharField(max_length=120, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, outstanding=None, **kwargs):
        self.outstanding = outstanding
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if self.outstanding is not None and amount > self.outstanding:
            raise forms.ValidationError(
                f"Amount cannot exceed the outstanding balance (Rs. {self.outstanding:,.2f})."
            )
        return amount
