from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import CreateView, DetailView, FormView

from apps.common.export import export_csv
from apps.common.models import InstallmentStatus, PaymentMethod
from apps.common.views import FilteredListView, ModalFormMixin, build_choice_filter
from apps.payments.forms import InstallmentPaymentForm, PaymentForm
from apps.payments.queries import due_installments_for_landlord, overdue_installments_for_landlord, payments_for_landlord
from apps.payments.services import record_installment_payment, record_payment, refresh_overdue_statuses


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
        return overdue_installments_for_landlord(self.request.user)


class InstallmentDetailView(LoginRequiredMixin, DetailView):
    template_name = "payments/installment_detail.html"
    context_object_name = "installment"

    def get_queryset(self) -> QuerySet:
        return due_installments_for_landlord(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installment = self.object
        total_billed = (
            installment.amount_due + installment.late_fee_amount + installment.adjustment_amount
        )
        context["total_billed"] = total_billed
        context["paid_percent"] = (
            round(installment.amount_paid / total_billed * 100) if total_billed else 0
        )
        return context


class InstallmentPaymentView(ModalFormMixin, LoginRequiredMixin, FormView):
    """Record a full or partial payment against a single installment."""

    form_class = InstallmentPaymentForm
    template_name = "payments/installment_payment_form.html"
    submit_label = "Record payment"
    modal_full_width_fields = "notes"

    @cached_property
    def installment(self):
        return get_object_or_404(due_installments_for_landlord(self.request.user), pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["outstanding"] = self.installment.outstanding_amount
        return kwargs

    def get_initial(self):
        return {"amount": self.installment.outstanding_amount}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installment = self.installment
        context["installment"] = installment
        context["modal_title"] = "Record payment"
        context["modal_description"] = (
            f"{installment.lease.property.name} · due {installment.due_date} · "
            f"outstanding Rs. {installment.outstanding_amount:,.2f}"
        )
        return context

    def form_valid(self, form):
        try:
            record_installment_payment(
                installment=self.installment,
                created_by=self.request.user,
                **form.cleaned_data,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Payment recorded against the installment.")
        url = self.installment.get_absolute_url()
        return self.modal_redirect(url) if self.is_modal_request() else redirect(url)


class InstallmentMarkPaidView(LoginRequiredMixin, View):
    """One-click: settle an installment's full outstanding balance."""

    def post(self, request, *args, **kwargs):
        installment = get_object_or_404(
            due_installments_for_landlord(request.user), pk=kwargs["pk"]
        )
        if installment.outstanding_amount > 0:
            record_installment_payment(
                installment=installment,
                amount=installment.outstanding_amount,
                payment_method=request.POST.get("payment_method") or PaymentMethod.BANK_TRANSFER,
                created_by=request.user,
            )
            messages.success(request, "Installment marked as paid in full.")
        else:
            messages.info(request, "This installment is already fully paid.")
        return redirect(installment.get_absolute_url())


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
