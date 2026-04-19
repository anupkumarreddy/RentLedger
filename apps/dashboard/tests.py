from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.dashboard.services import get_landlord_dashboard_summary
from apps.expenses.models import Expense
from apps.leases.models import Lease
from apps.payments.services import generate_payment_schedule, record_payment
from apps.properties.models import Property
from apps.tenants.models import Tenant


User = get_user_model()


class DashboardServiceTests(TestCase):
    def test_dashboard_summary_contains_core_metrics(self):
        landlord = User.objects.create_user(email="owner@example.com", password="StrongPass123", full_name="Owner")
        property_obj = Property.objects.create(
            landlord=landlord,
            name="A1",
            property_type="apartment",
            address_line_1="Street",
            city="Hyderabad",
            state="Telangana",
            country="India",
            rent_default="15000.00",
        )
        tenant = Tenant.objects.create(landlord=landlord, full_name="Tenant")
        lease = Lease.objects.create(
            landlord=landlord,
            property=property_obj,
            tenant=tenant,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 7, 1),
            rent_amount="15000.00",
            security_deposit="20000.00",
            payment_frequency="monthly",
            due_day=5,
            grace_days=3,
            late_fee_type="none",
            late_fee_value="0.00",
            status="active",
        )
        generate_payment_schedule(lease)
        record_payment(
            landlord=landlord,
            created_by=landlord,
            lease=lease,
            tenant=tenant,
            payment_date=date.today(),
            amount=Decimal("15000.00"),
            payment_method="upi",
            reference_number="UPI777",
            notes="Monthly rent",
            audit_note="Test payment",
        )
        Expense.objects.create(
            landlord=landlord,
            property=property_obj,
            expense_date=date.today(),
            category="maintenance",
            amount=Decimal("2000.00"),
            vendor_name="Vendor",
            payment_method="cash",
        )

        summary = get_landlord_dashboard_summary(landlord)
        self.assertEqual(summary["total_properties"], 1)
        self.assertEqual(summary["occupied_units"], 1)
        self.assertEqual(summary["monthly_collected_rent"], Decimal("15000.00"))
        self.assertEqual(summary["expenses_this_month"], Decimal("2000.00"))
