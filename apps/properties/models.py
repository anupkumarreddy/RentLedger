from django.db import models
from django.urls import reverse

from apps.common.models import IsActiveMixin, LandlordOwnedModel, PropertyType, TimeStampedModel


class Property(TimeStampedModel, IsActiveMixin, LandlordOwnedModel):
    name = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=120, default="India")
    rent_default = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["landlord", "is_active"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("properties:detail", args=[self.pk])
