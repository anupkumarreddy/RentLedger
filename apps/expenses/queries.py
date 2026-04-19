from django.db.models import Sum

from apps.expenses.models import Expense


def expense_queryset_for_landlord(landlord):
    return Expense.objects.filter(landlord=landlord).select_related("property")


def monthly_expense_total(landlord, start_date, end_date):
    return expense_queryset_for_landlord(landlord).filter(expense_date__range=(start_date, end_date)).aggregate(total=Sum("amount"))["total"] or 0
