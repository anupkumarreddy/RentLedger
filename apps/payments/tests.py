from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.common.models import LeaseStatus
from apps.leases.models import Lease
from apps.payments.services import generate_payment_schedule, record_payment
from apps.properties.models import Property
from apps.tenants.models import Tenant


User = get_user_model()


class PaymentServiceTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(email="owner@example.com", password="StrongPass123", full_name="Owner")
        self.property = Property.objects.create(
            landlord=self.landlord,
            name="Maple Residency",
            property_type="apartment",
            address_line_1="Street 1",
            city="Hyderabad",
            state="Telangana",
            country="India",
            rent_default="20000.00",
        )
        self.tenant = Tenant.objects.create(landlord=self.landlord, full_name="Tenant")
        self.lease = Lease.objects.create(
            landlord=self.landlord,
            property=self.property,
            tenant=self.tenant,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 1),
            rent_amount="20000.00",
            security_deposit="40000.00",
            payment_frequency="monthly",
            due_day=5,
            grace_days=365,
            late_fee_type="none",
            late_fee_value="0.00",
            status=LeaseStatus.ACTIVE,
        )
        generate_payment_schedule(self.lease)

    def test_partial_payment_updates_installment_balances(self):
        payment = record_payment(
            landlord=self.landlord,
            created_by=self.landlord,
            lease=self.lease,
            tenant=self.tenant,
            payment_date=date(2026, 4, 3),
            amount=Decimal("8000.00"),
            payment_method="upi",
            reference_number="UPI123",
            notes="Partial April rent",
            audit_note="Created for test",
        )
        installment = self.lease.installments.order_by("due_date").first()
        installment.refresh_from_db()
        self.assertEqual(payment.allocations.count(), 1)
        self.assertEqual(installment.amount_paid, Decimal("8000.00"))
        self.assertEqual(installment.outstanding_amount, Decimal("12000.00"))
        self.assertEqual(installment.status, "partial")

    def test_payment_allocates_across_multiple_installments(self):
        payment = record_payment(
            landlord=self.landlord,
            created_by=self.landlord,
            lease=self.lease,
            tenant=self.tenant,
            payment_date=date(2026, 4, 2),
            amount=Decimal("25000.00"),
            payment_method="bank_transfer",
            reference_number="BANK123",
            notes="Advance payment",
            audit_note="Created for test",
        )
        installments = list(self.lease.installments.order_by("due_date"))
        for installment in installments:
            installment.refresh_from_db()
        self.assertEqual(payment.allocations.count(), 2)
        self.assertEqual(installments[0].status, "paid")
        self.assertEqual(installments[0].outstanding_amount, Decimal("0.00"))
        self.assertEqual(installments[1].status, "partial")
        self.assertEqual(installments[1].amount_paid, Decimal("5000.00"))

    def test_negative_payment_is_rejected_by_validation(self):
        with self.assertRaises(ValidationError):
            record_payment(
                landlord=self.landlord,
                created_by=self.landlord,
                lease=self.lease,
                tenant=self.tenant,
                payment_date=date(2026, 4, 2),
                amount=Decimal("-1.00"),
                payment_method="bank_transfer",
                reference_number="BANK123",
                notes="Invalid payment",
                audit_note="Created for test",
            )

    def test_overdue_fixed_late_fee_is_assessed_before_allocation(self):
        lease = Lease.objects.create(
            landlord=self.landlord,
            property=self.property,
            tenant=self.tenant,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 2, 1),
            rent_amount="10000.00",
            security_deposit="0.00",
            payment_frequency="monthly",
            due_day=1,
            grace_days=0,
            late_fee_type="fixed",
            late_fee_value="500.00",
            status=LeaseStatus.ACTIVE,
        )
        generate_payment_schedule(lease)

        record_payment(
            landlord=self.landlord,
            created_by=self.landlord,
            lease=lease,
            tenant=self.tenant,
            payment_date=timezone.localdate(),
            amount=Decimal("10000.00"),
            payment_method="bank_transfer",
            reference_number="BANK124",
            notes="Late payment",
            audit_note="Created for test",
        )

        installment = lease.installments.get()
        installment.refresh_from_db()
        self.assertEqual(installment.late_fee_amount, Decimal("500.00"))
        self.assertEqual(installment.outstanding_amount, Decimal("500.00"))
