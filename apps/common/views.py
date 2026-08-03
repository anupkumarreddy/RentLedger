from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import ListView


class ModalFormMixin:
    """Render create/update forms as an htmx-driven modal.

    When the request carries the ``HX-Request`` header (i.e. the form was
    opened via htmx into ``#modal-root``), the generic modal partial is used
    and a successful submit returns a 204 with an ``HX-Redirect`` header so the
    browser performs a full navigation to the success URL. Direct visits to the
    same URL keep working as normal full-page forms (progressive enhancement).
    """

    modal_title = ""
    modal_description = ""
    submit_label = "Save"
    modal_full_width_fields = ""
    modal_enctype = ""

    def is_modal_request(self):
        return self.request.headers.get("HX-Request") == "true"

    def get_template_names(self):
        if self.is_modal_request():
            return ["includes/ui/form_modal.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("modal_title", self.modal_title)
        context.setdefault("modal_description", self.modal_description)
        context.setdefault("submit_label", self.submit_label)
        context.setdefault("modal_full_width_fields", self.modal_full_width_fields)
        context.setdefault("modal_enctype", self.modal_enctype)
        context.setdefault("form_action", self.request.get_full_path())
        return context

    def modal_redirect(self, url):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = url
        return response


class FilteredListView(LoginRequiredMixin, ListView):
    """ListView with landlord-scoped search, dropdown filters and pagination.

    Subclasses implement :meth:`base_queryset` and may set ``search_fields``
    and/or override :meth:`apply_filters` / :meth:`get_filters`.
    """

    paginate_by = 12
    search_fields = []
    search_placeholder = "Search..."

    def base_queryset(self):
        raise NotImplementedError

    def apply_filters(self, queryset):
        return queryset

    def get_search_term(self):
        return self.request.GET.get("q", "").strip()

    def get_queryset(self):
        queryset = self.base_queryset()
        term = self.get_search_term()
        if term and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__icontains": term})
            queryset = queryset.filter(condition)
        return self.apply_filters(queryset)

    def get_filters(self):
        """Return a list of filter definitions for the toolbar.

        Each item: {"name", "label", "options": [{"value", "label", "selected"}]}.
        """
        return []

    def has_active_filters(self):
        keys = ["q"] + [f["name"] for f in self.get_filters()]
        return any(self.request.GET.get(key) for key in keys)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.get_search_term()
        context["search_placeholder"] = self.search_placeholder
        context["filters"] = self.get_filters()
        context["has_active_filters"] = self.has_active_filters()
        return context


def build_choice_filter(name, label, choices, selected):
    """Helper to build a filter dict from Django ``TextChoices``/tuples."""
    return {
        "name": name,
        "label": label,
        "options": [
            {"value": value, "label": text, "selected": str(selected) == str(value)}
            for value, text in choices
        ],
    }
