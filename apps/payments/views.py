from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from django.db.models import QuerySet

from apps.payments.forms import PaymentForm
from apps.payments.queries import due_installments_for_landlord, payments_for_landlord
from apps.payments.services import record_payment, refresh_overdue_statuses


class DueListView(LoginRequiredMixin, ListView):
    template_name = "payments/due_list.html"
    context_object_name = "installments"

    def get_queryset(self) -> QuerySet:
        refresh_overdue_statuses(self.request.user)
        return due_installments_for_landlord(self.request.user)


class OverdueListView(LoginRequiredMixin, ListView):
    template_name = "payments/overdue_list.html"
    context_object_name = "installments"

    def get_queryset(self) -> QuerySet:
        refresh_overdue_statuses(self.request.user)
        installments = due_installments_for_landlord(self.request.user)
        overdue_ids = [item.pk for item in installments if item.is_overdue_now]
        return installments.filter(pk__in=overdue_ids)


class InstallmentDetailView(LoginRequiredMixin, DetailView):
    template_name = "payments/installment_detail.html"
    context_object_name = "installment"

    def get_queryset(self) -> QuerySet:
        return due_installments_for_landlord(self.request.user)


class PaymentHistoryView(LoginRequiredMixin, ListView):
    template_name = "payments/payment_history.html"
    context_object_name = "payments"

    def get_queryset(self) -> QuerySet:
        return payments_for_landlord(self.request.user)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    form_class = PaymentForm
    template_name = "payments/payment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form) -> HttpResponseRedirect:
        payload = dict(form.cleaned_data)
        payload["landlord"] = self.request.user
        payload["created_by"] = self.request.user
        self.object = record_payment(**payload)
        messages.success(self.request, "Payment recorded and allocated.")
        return HttpResponseRedirect(reverse("payments:history"))
