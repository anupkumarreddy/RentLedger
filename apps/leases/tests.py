from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.common.models import LeaseStatus
from apps.leases.models import Lease
from apps.leases.services import activate_lease, create_lease
from apps.properties.models import Property
from apps.tenants.models import Tenant


User = get_user_model()


class LeaseServiceTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(email="owner@example.com", password="StrongPass123", full_name="Owner")
        self.property = Property.objects.create(
            landlord=self.landlord,
            name="Skyline 3A",
            property_type="apartment",
            address_line_1="Main road",
            city="Hyderabad",
            state="Telangana",
            country="India",
            rent_default="20000.00",
        )
        self.tenant = Tenant.objects.create(landlord=self.landlord, full_name="Tenant One")

    def test_active_lease_generates_installments(self):
        lease = create_lease(
            landlord=self.landlord,
            property=self.property,
            tenant=self.tenant,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 7, 1),
            rent_amount="20000.00",
            security_deposit="40000.00",
            payment_frequency="monthly",
            due_day=5,
            grace_days=3,
            late_fee_type="none",
            late_fee_value="0.00",
            status=LeaseStatus.ACTIVE,
            notes="",
            lease_document="",
        )
        self.assertEqual(lease.installments.count(), 3)

    def test_overlapping_active_leases_are_rejected(self):
        Lease.objects.create(
            landlord=self.landlord,
            property=self.property,
            tenant=self.tenant,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 1),
            rent_amount="20000.00",
            security_deposit="20000.00",
            payment_frequency="monthly",
            due_day=5,
            grace_days=2,
            late_fee_type="none",
            late_fee_value="0.00",
            status=LeaseStatus.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            create_lease(
                landlord=self.landlord,
                property=self.property,
                tenant=self.tenant,
                start_date=date(2026, 5, 1),
                end_date=date(2026, 8, 1),
                rent_amount="22000.00",
                security_deposit="20000.00",
                payment_frequency="monthly",
                due_day=5,
                grace_days=2,
                late_fee_type="none",
                late_fee_value="0.00",
                status=LeaseStatus.ACTIVE,
                notes="",
                lease_document="",
            )
