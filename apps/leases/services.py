from django.core.exceptions import ValidationError
from django.db import transaction

from apps.common.models import LeaseStatus
from apps.leases.models import Lease
from apps.leases.queries import active_leases_for_property
from apps.payments.services import generate_payment_schedule


def validate_no_overlap(*, property_obj, start_date, end_date, exclude_lease_id=None):
    overlaps = active_leases_for_property(property_obj, exclude_lease_id=exclude_lease_id).filter(
        start_date__lt=end_date,
        end_date__gt=start_date,
    )
    if overlaps.exists():
        raise ValidationError("This property already has an overlapping active lease for the selected period.")


@transaction.atomic
def create_lease(*, landlord, **data):
    property_obj = data["property"]
    tenant = data["tenant"]
    if property_obj.landlord_id != landlord.id or tenant.landlord_id != landlord.id:
        raise ValidationError("Property and tenant must belong to the current landlord.")

    if data.get("status") == LeaseStatus.ACTIVE:
        validate_no_overlap(property_obj=property_obj, start_date=data["start_date"], end_date=data["end_date"])

    lease = Lease.objects.create(landlord=landlord, **data)
    if lease.status == LeaseStatus.ACTIVE:
        generate_payment_schedule(lease)
    return lease


@transaction.atomic
def activate_lease(*, lease, activated_by=None):
    validate_no_overlap(property_obj=lease.property, start_date=lease.start_date, end_date=lease.end_date, exclude_lease_id=lease.id)
    if lease.status != LeaseStatus.ACTIVE:
        lease.status = LeaseStatus.ACTIVE
        lease.save(update_fields=["status", "updated_at"])
    if not lease.installments.exists():
        generate_payment_schedule(lease)
    return lease


@transaction.atomic
def terminate_lease(*, lease):
    lease.status = LeaseStatus.TERMINATED
    lease.save(update_fields=["status", "updated_at"])
    return lease
