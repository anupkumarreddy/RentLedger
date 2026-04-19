from apps.common.forms import BaseStyledForm, DateInput
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
