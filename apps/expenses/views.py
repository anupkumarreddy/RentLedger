from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView

from apps.common.export import export_csv
from apps.common.models import ExpenseCategory
from apps.common.views import FilteredListView, ModalFormMixin, build_choice_filter
from apps.expenses.forms import ExpenseForm
from apps.expenses.queries import expense_queryset_for_landlord, monthly_expense_total
from apps.expenses.services import record_expense


class ExpenseListView(FilteredListView):
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"
    search_fields = ["vendor_name", "notes", "property__name"]
    search_placeholder = "Search by vendor, note or property"

    def base_queryset(self):
        return expense_queryset_for_landlord(self.request.user)

    def apply_filters(self, queryset):
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_filters(self):
        return [
            build_choice_filter("category", "All categories", ExpenseCategory.choices, self.request.GET.get("category")),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start = today.replace(day=1)
        context["monthly_total"] = monthly_expense_total(self.request.user, start, today)
        return context


class ExpenseExportView(ExpenseListView):
    def get(self, request, *args, **kwargs):
        rows = []
        for expense in self.get_queryset():
            rows.append(
                [
                    expense.expense_date,
                    expense.get_category_display(),
                    expense.property.name if expense.property else "Unassigned",
                    expense.vendor_name,
                    expense.get_payment_method_display(),
                    expense.amount,
                ]
            )
        return export_csv(
            "expenses",
            ["Date", "Category", "Property", "Vendor", "Method", "Amount"],
            rows,
        )


class ExpenseCreateView(ModalFormMixin, LoginRequiredMixin, CreateView):
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"
    modal_title = "Add expense"
    modal_description = "Capture category, property, payment channel, and notes."
    submit_label = "Save expense"
    modal_full_width_fields = "notes,attachment"
    modal_enctype = "multipart/form-data"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = record_expense(landlord=self.request.user, **form.cleaned_data)
        messages.success(self.request, "Expense recorded.")
        url = reverse("expenses:list")
        return self.modal_redirect(url) if self.is_modal_request() else redirect(url)
