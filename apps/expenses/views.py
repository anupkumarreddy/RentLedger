from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, ListView

from apps.expenses.forms import ExpenseForm
from apps.expenses.queries import expense_queryset_for_landlord, monthly_expense_total
from apps.expenses.services import record_expense


class ExpenseListView(LoginRequiredMixin, ListView):
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return expense_queryset_for_landlord(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start = today.replace(day=1)
        context["monthly_total"] = monthly_expense_total(self.request.user, start, today)
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = record_expense(landlord=self.request.user, **form.cleaned_data)
        messages.success(self.request, "Expense recorded.")
        return redirect("expenses:list")
