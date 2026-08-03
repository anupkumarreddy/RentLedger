from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from apps.common.models import PropertyType
from apps.common.views import FilteredListView, ModalFormMixin, build_choice_filter
from apps.properties.forms import PropertyForm
from apps.properties.queries import property_detail_context, property_queryset_for_landlord


class PropertyQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return property_queryset_for_landlord(self.request.user)


class PropertyListView(FilteredListView):
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    search_fields = ["name", "address_line_1", "city", "state"]
    search_placeholder = "Search by name, address or city"

    def base_queryset(self):
        return property_queryset_for_landlord(self.request.user)

    def apply_filters(self, queryset):
        prop_type = self.request.GET.get("type")
        if prop_type:
            queryset = queryset.filter(property_type=prop_type)
        occupancy = self.request.GET.get("occupancy")
        if occupancy == "occupied":
            queryset = queryset.filter(is_occupied=True)
        elif occupancy == "vacant":
            queryset = queryset.filter(is_occupied=False)
        return queryset

    def get_filters(self):
        return [
            build_choice_filter("type", "All types", PropertyType.choices, self.request.GET.get("type")),
            build_choice_filter(
                "occupancy",
                "All units",
                [("occupied", "Occupied"), ("vacant", "Vacant")],
                self.request.GET.get("occupancy"),
            ),
        ]


class PropertyDetailView(PropertyQuerysetMixin, DetailView):
    template_name = "properties/property_detail.html"
    context_object_name = "property"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(property_detail_context(self.object))
        return context


class PropertyCreateView(ModalFormMixin, LoginRequiredMixin, CreateView):
    form_class = PropertyForm
    template_name = "properties/property_form.html"
    modal_title = "Add property"
    modal_description = "Capture location, type, and rent defaults for this unit."
    submit_label = "Save property"
    modal_full_width_fields = "address_line_1,address_line_2,notes"

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Property created.")
        if self.is_modal_request():
            return self.modal_redirect(self.get_success_url())
        return response


class PropertyUpdateView(ModalFormMixin, PropertyQuerysetMixin, UpdateView):
    form_class = PropertyForm
    template_name = "properties/property_form.html"
    modal_title = "Edit property"
    modal_description = "Update location, type, and rent defaults for this unit."
    submit_label = "Save changes"
    modal_full_width_fields = "address_line_1,address_line_2,notes"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Property updated.")
        if self.is_modal_request():
            return self.modal_redirect(self.get_success_url())
        return response


class PropertyArchiveView(PropertyQuerysetMixin, View):
    def post(self, request, *args, **kwargs):
        property_obj = self.get_queryset().get(pk=kwargs["pk"])
        property_obj.is_active = not property_obj.is_active
        property_obj.save(update_fields=["is_active", "updated_at"])
        messages.success(
            request,
            "Property restored." if property_obj.is_active else "Property archived.",
        )
        return redirect(property_obj.get_absolute_url())
