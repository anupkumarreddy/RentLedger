from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.tenants.forms import TenantForm
from apps.tenants.queries import tenant_queryset_for_landlord


class TenantQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return tenant_queryset_for_landlord(self.request.user)


class TenantListView(TenantQuerysetMixin, ListView):
    template_name = "tenants/tenant_list.html"
    context_object_name = "tenants"


class TenantDetailView(TenantQuerysetMixin, DetailView):
    template_name = "tenants/tenant_detail.html"
    context_object_name = "tenant"


class TenantCreateView(LoginRequiredMixin, CreateView):
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        messages.success(self.request, "Tenant created.")
        return super().form_valid(form)


class TenantUpdateView(TenantQuerysetMixin, UpdateView):
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Tenant updated.")
        return super().form_valid(form)
