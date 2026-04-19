from django.urls import path

from apps.properties.views import PropertyCreateView, PropertyDetailView, PropertyListView, PropertyUpdateView


app_name = "properties"

urlpatterns = [
    path("", PropertyListView.as_view(), name="list"),
    path("add/", PropertyCreateView.as_view(), name="create"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", PropertyUpdateView.as_view(), name="edit"),
]
