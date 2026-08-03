from django.urls import path

from apps.tenants.views import (
    TenantArchiveView,
    TenantCreateView,
    TenantDetailView,
    TenantListView,
    TenantUpdateView,
)


app_name = "tenants"

urlpatterns = [
    path("", TenantListView.as_view(), name="list"),
    path("add/", TenantCreateView.as_view(), name="create"),
    path("<int:pk>/", TenantDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", TenantUpdateView.as_view(), name="edit"),
    path("<int:pk>/archive/", TenantArchiveView.as_view(), name="archive"),
]
