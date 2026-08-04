from django.urls import path

from apps.payments.views import (
    DueListView,
    InstallmentDetailView,
    InstallmentMarkPaidView,
    InstallmentPaymentView,
    OverdueListView,
    PaymentCreateView,
    PaymentExportView,
    PaymentHistoryView,
)


app_name = "payments"

urlpatterns = [
    path("dues/", DueListView.as_view(), name="due_list"),
    path("overdue/", OverdueListView.as_view(), name="overdue_list"),
    path("history/", PaymentHistoryView.as_view(), name="history"),
    path("history/export/", PaymentExportView.as_view(), name="export"),
    path("record/", PaymentCreateView.as_view(), name="create"),
    path("installments/<int:pk>/", InstallmentDetailView.as_view(), name="installment_detail"),
    path("installments/<int:pk>/pay/", InstallmentPaymentView.as_view(), name="installment_pay"),
    path("installments/<int:pk>/mark-paid/", InstallmentMarkPaidView.as_view(), name="installment_mark_paid"),
]
