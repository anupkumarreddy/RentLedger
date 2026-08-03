from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from apps.common.views import FilteredListView, ModalFormMixin
from apps.tenants.forms import TenantForm
from apps.tenants.queries import tenant_detail_context, tenant_queryset_for_landlord


class TenantQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return tenant_queryset_for_landlord(self.request.user)


class TenantListView(FilteredListView):
    template_name = "tenants/tenant_list.html"
    context_object_name = "tenants"
    search_fields = ["full_name", "email", "phone", "government_id_value"]
    search_placeholder = "Search by name, email or phone"

    def base_queryset(self):
        return tenant_queryset_for_landlord(self.request.user)

    def apply_filters(self, queryset):
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_filters(self):
        selected = self.request.GET.get("status")
        return [
            {
                "name": "status",
                "label": "All tenants",
                "options": [
                    {"value": "active", "label": "Active", "selected": selected == "active"},
                    {"value": "inactive", "label": "Archived", "selected": selected == "inactive"},
                ],
            }
        ]


class TenantDetailView(TenantQuerysetMixin, DetailView):
    template_name = "tenants/tenant_detail.html"
    context_object_name = "tenant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(tenant_detail_context(self.object))
        return context


class TenantCreateView(ModalFormMixin, LoginRequiredMixin, CreateView):
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"
    modal_title = "Add tenant"
    modal_description = "Capture contact details, identity records, and notes."
    submit_label = "Save tenant"
    modal_full_width_fields = "current_address,notes"

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Tenant created.")
        if self.is_modal_request():
            return self.modal_redirect(self.get_success_url())
        return response


class TenantUpdateView(ModalFormMixin, TenantQuerysetMixin, UpdateView):
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"
    modal_title = "Edit tenant"
    modal_description = "Update contact details, identity records, and notes."
    submit_label = "Save changes"
    modal_full_width_fields = "current_address,notes"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Tenant updated.")
        if self.is_modal_request():
            return self.modal_redirect(self.get_success_url())
        return response


class TenantArchiveView(TenantQuerysetMixin, View):
    def post(self, request, *args, **kwargs):
        tenant = self.get_queryset().get(pk=kwargs["pk"])
        tenant.is_active = not tenant.is_active
        tenant.save(update_fields=["is_active", "updated_at"])
        messages.success(
            request,
            "Tenant restored." if tenant.is_active else "Tenant archived.",
        )
        return redirect(tenant.get_absolute_url())
