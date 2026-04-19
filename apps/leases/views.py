from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.leases.forms import LeaseForm
from apps.leases.models import Lease
from apps.leases.queries import lease_queryset_for_landlord
from apps.leases.services import activate_lease, create_lease, terminate_lease


class LeaseQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return lease_queryset_for_landlord(self.request.user)


class LeaseListView(LeaseQuerysetMixin, ListView):
    template_name = "leases/lease_list.html"
    context_object_name = "leases"


class LeaseDetailView(LeaseQuerysetMixin, DetailView):
    template_name = "leases/lease_detail.html"
    context_object_name = "lease"


class LeaseCreateView(LoginRequiredMixin, CreateView):
    form_class = LeaseForm
    template_name = "leases/lease_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = create_lease(landlord=self.request.user, **form.cleaned_data)
        messages.success(self.request, "Lease saved.")
        return redirect(self.object.get_absolute_url())


class LeaseUpdateView(LeaseQuerysetMixin, UpdateView):
    form_class = LeaseForm
    template_name = "leases/lease_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        for field, value in form.cleaned_data.items():
            setattr(self.object, field, value)
        self.object.landlord = self.request.user
        self.object.full_clean()
        self.object.save()
        messages.success(self.request, "Lease updated.")
        return redirect(self.object.get_absolute_url())


class LeaseActivateView(LeaseQuerysetMixin, View):
    def post(self, request, *args, **kwargs):
        lease = self.get_queryset().get(pk=kwargs["pk"])
        activate_lease(lease=lease, activated_by=request.user)
        messages.success(request, "Lease activated and schedule generated.")
        return redirect(lease.get_absolute_url())


class LeaseTerminateView(LeaseQuerysetMixin, View):
    def post(self, request, *args, **kwargs):
        lease = self.get_queryset().get(pk=kwargs["pk"])
        terminate_lease(lease=lease)
        messages.success(request, "Lease terminated.")
        return redirect(lease.get_absolute_url())
