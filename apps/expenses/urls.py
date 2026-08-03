from django.urls import path

from apps.expenses.views import ExpenseCreateView, ExpenseExportView, ExpenseListView


app_name = "expenses"

urlpatterns = [
    path("", ExpenseListView.as_view(), name="list"),
    path("add/", ExpenseCreateView.as_view(), name="create"),
    path("export/", ExpenseExportView.as_view(), name="export"),
]
