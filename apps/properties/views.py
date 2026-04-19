from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.properties.forms import PropertyForm
from apps.properties.models import Property
from apps.properties.queries import property_queryset_for_landlord


class PropertyQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return property_queryset_for_landlord(self.request.user)


class PropertyListView(PropertyQuerysetMixin, ListView):
    template_name = "properties/property_list.html"
    context_object_name = "properties"


class PropertyDetailView(PropertyQuerysetMixin, DetailView):
    template_name = "properties/property_detail.html"
    context_object_name = "property"


class PropertyCreateView(LoginRequiredMixin, CreateView):
    form_class = PropertyForm
    template_name = "properties/property_form.html"

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        messages.success(self.request, "Property created.")
        return super().form_valid(form)


class PropertyUpdateView(PropertyQuerysetMixin, UpdateView):
    form_class = PropertyForm
    template_name = "properties/property_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Property updated.")
        return super().form_valid(form)
