from django.urls import path

from apps.payments.views import DueListView, InstallmentDetailView, OverdueListView, PaymentCreateView, PaymentHistoryView


app_name = "payments"

urlpatterns = [
    path("dues/", DueListView.as_view(), name="due_list"),
    path("overdue/", OverdueListView.as_view(), name="overdue_list"),
    path("history/", PaymentHistoryView.as_view(), name="history"),
    path("record/", PaymentCreateView.as_view(), name="create"),
    path("installments/<int:pk>/", InstallmentDetailView.as_view(), name="installment_detail"),
]
