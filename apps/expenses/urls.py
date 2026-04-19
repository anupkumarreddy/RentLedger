from django.urls import path

from apps.expenses.views import ExpenseCreateView, ExpenseListView


app_name = "expenses"

urlpatterns = [
    path("", ExpenseListView.as_view(), name="list"),
    path("add/", ExpenseCreateView.as_view(), name="create"),
]
