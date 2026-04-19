from django.db import models
from django.urls import reverse

from apps.common.models import IsActiveMixin, LandlordOwnedModel, TimeStampedModel


class Tenant(TimeStampedModel, IsActiveMixin, LandlordOwnedModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    government_id_type = models.CharField(max_length=50, blank=True)
    government_id_value = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    current_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [models.Index(fields=["landlord", "is_active"])]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("tenants:detail", args=[self.pk])
