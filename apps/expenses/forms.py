from apps.common.forms import BaseStyledForm, DateInput
from apps.expenses.models import Expense


class ExpenseForm(BaseStyledForm):
    class Meta:
        model = Expense
        exclude = ["landlord", "created_at", "updated_at"]
        widgets = {"expense_date": DateInput()}

    def __init__(self, *args, landlord=None, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord is not None:
            self.fields["property"].queryset = self.fields["property"].queryset.filter(landlord=landlord)
