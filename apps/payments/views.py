from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView

from apps.common.export import export_csv
from apps.common.models import InstallmentStatus, PaymentMethod
from apps.common.views import FilteredListView, ModalFormMixin, build_choice_filter
from apps.payments.forms import PaymentForm
from apps.payments.queries import due_installments_for_landlord, payments_for_landlord
from apps.payments.services import record_payment, refresh_overdue_statuses


class DueListView(FilteredListView):
    template_name = "payments/due_list.html"
    context_object_name = "installments"
    search_fields = ["lease__property__name", "lease__tenant__full_name"]
    search_placeholder = "Search by property or tenant"

    def base_queryset(self) -> QuerySet:
        refresh_overdue_statuses(self.request.user)
        return due_installments_for_landlord(self.request.user)

    def apply_filters(self, queryset):
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_filters(self):
        return [
            build_choice_filter("status", "All statuses", InstallmentStatus.choices, self.request.GET.get("status")),
        ]


class OverdueListView(FilteredListView):
    template_name = "payments/overdue_list.html"
    context_object_name = "installments"
    search_fields = ["lease__property__name", "lease__tenant__full_name"]
    search_placeholder = "Search by property or tenant"

    def base_queryset(self) -> QuerySet:
        refresh_overdue_statuses(self.request.user)
        return due_installments_for_landlord(self.request.user).filter(
            status=InstallmentStatus.OVERDUE
        )


class InstallmentDetailView(LoginRequiredMixin, DetailView):
    template_name = "payments/installment_detail.html"
    context_object_name = "installment"

    def get_queryset(self) -> QuerySet:
        return due_installments_for_landlord(self.request.user)


class PaymentHistoryView(FilteredListView):
    template_name = "payments/payment_history.html"
    context_object_name = "payments"
    search_fields = ["lease__property__name", "tenant__full_name", "reference_number"]
    search_placeholder = "Search by property, tenant or reference"

    def base_queryset(self) -> QuerySet:
        return payments_for_landlord(self.request.user).select_related("lease__property")

    def apply_filters(self, queryset):
        method = self.request.GET.get("method")
        if method:
            queryset = queryset.filter(payment_method=method)
        return queryset

    def get_filters(self):
        return [
            build_choice_filter("method", "All methods", PaymentMethod.choices, self.request.GET.get("method")),
        ]


class PaymentExportView(PaymentHistoryView):
    """CSV export honouring the active search/method filters."""

    def get(self, request, *args, **kwargs):
        rows = []
        for payment in self.get_queryset():
            rows.append(
                [
                    payment.payment_date,
                    payment.lease.property.name,
                    payment.tenant.full_name,
                    payment.get_payment_method_display(),
                    payment.reference_number,
                    payment.amount,
                ]
            )
        return export_csv(
            "payments",
            ["Date", "Property", "Tenant", "Method", "Reference", "Amount"],
            rows,
        )


class PaymentCreateView(ModalFormMixin, LoginRequiredMixin, CreateView):
    form_class = PaymentForm
    template_name = "payments/payment_form.html"
    modal_title = "Record payment"
    modal_description = "Payments are auto-allocated against the oldest outstanding installments."
    submit_label = "Save payment"
    modal_full_width_fields = "notes,audit_note"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        payload = dict(form.cleaned_data)
        payload["landlord"] = self.request.user
        payload["created_by"] = self.request.user
        self.object = record_payment(**payload)
        messages.success(self.request, "Payment recorded and allocated.")
        url = reverse("payments:history")
        return self.modal_redirect(url) if self.is_modal_request() else HttpResponseRedirect(url)
