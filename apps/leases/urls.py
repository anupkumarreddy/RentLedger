from django.urls import path

from apps.leases.views import LeaseActivateView, LeaseCreateView, LeaseDetailView, LeaseListView, LeaseTerminateView, LeaseUpdateView


app_name = "leases"

urlpatterns = [
    path("", LeaseListView.as_view(), name="list"),
    path("add/", LeaseCreateView.as_view(), name="create"),
    path("<int:pk>/", LeaseDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", LeaseUpdateView.as_view(), name="edit"),
    path("<int:pk>/activate/", LeaseActivateView.as_view(), name="activate"),
    path("<int:pk>/terminate/", LeaseTerminateView.as_view(), name="terminate"),
]
