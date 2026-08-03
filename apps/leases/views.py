from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from apps.common.models import LeaseStatus
from apps.common.views import FilteredListView, ModalFormMixin, build_choice_filter
from apps.leases.forms import LeaseForm
from apps.leases.queries import lease_detail_context, lease_queryset_for_landlord
from apps.leases.services import activate_lease, create_lease, terminate_lease


class LeaseQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return lease_queryset_for_landlord(self.request.user)


class LeaseListView(FilteredListView):
    template_name = "leases/lease_list.html"
    context_object_name = "leases"
    search_fields = ["property__name", "tenant__full_name"]
    search_placeholder = "Search by property or tenant"

    def base_queryset(self):
        return lease_queryset_for_landlord(self.request.user)

    def apply_filters(self, queryset):
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_filters(self):
        return [
            build_choice_filter("status", "All statuses", LeaseStatus.choices, self.request.GET.get("status")),
        ]


class LeaseDetailView(LeaseQuerysetMixin, DetailView):
    template_name = "leases/lease_detail.html"
    context_object_name = "lease"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(lease_detail_context(self.object))
        return context


class LeaseCreateView(ModalFormMixin, LoginRequiredMixin, CreateView):
    form_class = LeaseForm
    template_name = "leases/lease_form.html"
    modal_title = "Create lease"
    modal_description = "Connect a property and tenant, then define rent and billing rules."
    submit_label = "Save lease"
    modal_full_width_fields = "notes,lease_document"
    modal_enctype = "multipart/form-data"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["landlord"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = create_lease(landlord=self.request.user, **form.cleaned_data)
        messages.success(self.request, "Lease saved.")
        url = self.object.get_absolute_url()
        return self.modal_redirect(url) if self.is_modal_request() else redirect(url)


class LeaseUpdateView(ModalFormMixin, LeaseQuerysetMixin, UpdateView):
    form_class = LeaseForm
    template_name = "leases/lease_form.html"
    modal_title = "Edit lease"
    modal_description = "Update rent, billing rules, contract dates, and documentation."
    submit_label = "Save changes"
    modal_full_width_fields = "notes,lease_document"
    modal_enctype = "multipart/form-data"

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
        url = self.object.get_absolute_url()
        return self.modal_redirect(url) if self.is_modal_request() else redirect(url)


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
