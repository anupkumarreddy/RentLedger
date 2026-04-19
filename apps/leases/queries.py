from django.apps import apps

from apps.common.models import LeaseStatus


def lease_queryset_for_landlord(landlord):
    Lease = apps.get_model("leases", "Lease")
    return Lease.objects.filter(landlord=landlord).select_related("property", "tenant")


def active_leases_for_property(property_obj, *, exclude_lease_id=None):
    Lease = apps.get_model("leases", "Lease")
    queryset = Lease.objects.filter(property=property_obj, status=LeaseStatus.ACTIVE)
    if exclude_lease_id:
        queryset = queryset.exclude(pk=exclude_lease_id)
    return queryset
