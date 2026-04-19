from apps.common.forms import BaseStyledForm, DateInput
from apps.leases.models import Lease


class LeaseForm(BaseStyledForm):
    class Meta:
        model = Lease
        exclude = ["landlord", "created_at", "updated_at"]
        widgets = {
            "start_date": DateInput(),
            "end_date": DateInput(),
        }

    def __init__(self, *args, landlord=None, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord is not None:
            self.fields["property"].queryset = self.fields["property"].queryset.filter(landlord=landlord)
            self.fields["tenant"].queryset = self.fields["tenant"].queryset.filter(landlord=landlord)
