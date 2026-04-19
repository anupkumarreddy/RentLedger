from django.apps import apps
from django.db.models import Exists, OuterRef

from apps.common.models import LeaseStatus
from apps.properties.models import Property


def property_queryset_for_landlord(landlord):
    Lease = apps.get_model("leases", "Lease")
    active_lease = Lease.objects.filter(
        landlord=landlord,
        property=OuterRef("pk"),
        status=LeaseStatus.ACTIVE,
    )
    return Property.objects.filter(landlord=landlord).annotate(is_occupied=Exists(active_lease))
