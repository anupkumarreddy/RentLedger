from django.core.exceptions import ValidationError

from apps.expenses.models import Expense


def record_expense(*, landlord, **data):
    property_obj = data.get("property")
    if property_obj and property_obj.landlord_id != landlord.id:
        raise ValidationError("Property must belong to the current landlord.")
    expense = Expense(landlord=landlord, **data)
    expense.full_clean()
    expense.save()
    return expense
