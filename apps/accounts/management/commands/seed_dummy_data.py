from datetime import date, timedelta
from decimal import Decimal
from random import Random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.common.models import ExpenseCategory, LateFeeType, LeaseStatus, PaymentFrequency, PaymentMethod, PropertyType
from apps.expenses.models import Expense
from apps.leases.models import Lease
from apps.payments.models import Payment
from apps.payments.services import generate_payment_schedule, record_payment
from apps.properties.models import Property
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = "Seed the database with landlord-scoped dummy data for local testing."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10, help="Number of records to create for each main entity.")
        parser.add_argument("--reset", action="store_true", help="Delete existing seeded demo records before creating new ones.")

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]
        rng = Random(42)

        if reset:
            self._reset_seeded_data()

        landlord = self._get_or_create_landlord()
        properties = self._create_properties(landlord, count, rng)
        tenants = self._create_tenants(landlord, count)
        leases = self._create_leases(landlord, properties, tenants, count, rng)
        payments = self._create_payments(landlord, leases, count, rng)
        expenses = self._create_expenses(landlord, properties, count, rng)

        self.stdout.write(self.style.SUCCESS("Dummy data created successfully."))
        self.stdout.write(f"Landlord: {landlord.email}")
        self.stdout.write(f"Properties: {len(properties)}")
        self.stdout.write(f"Tenants: {len(tenants)}")
        self.stdout.write(f"Leases: {len(leases)}")
        self.stdout.write(f"Payments: {len(payments)}")
        self.stdout.write(f"Expenses: {len(expenses)}")

    def _reset_seeded_data(self):
        Payment.objects.filter(landlord__email__startswith="demo.landlord").delete()
        Expense.objects.filter(landlord__email__startswith="demo.landlord").delete()
        Lease.objects.filter(landlord__email__startswith="demo.landlord").delete()
        Property.objects.filter(landlord__email__startswith="demo.landlord").delete()
        Tenant.objects.filter(landlord__email__startswith="demo.landlord").delete()
        User.objects.filter(email__startswith="demo.landlord").delete()

    def _get_or_create_landlord(self):
        landlord, created = User.objects.get_or_create(
            email="demo.landlord@example.com",
            defaults={
                "full_name": "Demo Landlord",
                "phone": "+91-9876500000",
                "is_active": True,
            },
        )
        if created:
            landlord.set_password("DemoPass123")
            landlord.save(update_fields=["password"])
        return landlord

    def _create_properties(self, landlord, count, rng):
        properties = []
        property_types = list(PropertyType.values)
        for index in range(count):
            property_obj, _ = Property.objects.get_or_create(
                landlord=landlord,
                name=f"Demo Property {index + 1}",
                defaults={
                    "property_type": property_types[index % len(property_types)],
                    "address_line_1": f"{100 + index} Palm Residency",
                    "address_line_2": f"Block {chr(65 + (index % 5))}",
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "postal_code": f"5000{index:02d}",
                    "country": "India",
                    "rent_default": Decimal("15000.00") + (Decimal(index) * Decimal("1500.00")),
                    "notes": "Seeded property for UI testing.",
                },
            )
            properties.append(property_obj)
        return properties

    def _create_tenants(self, landlord, count):
        tenants = []
        for index in range(count):
            tenant, _ = Tenant.objects.get_or_create(
                landlord=landlord,
                full_name=f"Demo Tenant {index + 1}",
                defaults={
                    "email": f"tenant{index + 1}@example.com",
                    "phone": f"9000000{index:03d}",
                    "government_id_type": "Aadhaar",
                    "government_id_value": f"XXXX-XXXX-{1000 + index}",
                    "emergency_contact": f"Emergency Contact {index + 1}",
                    "current_address": f"Flat {index + 1}, Demo Residency, Hyderabad",
                    "notes": "Seeded tenant for UI testing.",
                },
            )
            tenants.append(tenant)
        return tenants

    def _create_leases(self, landlord, properties, tenants, count, rng):
        leases = []
        today = date.today()
        for index in range(count):
            start_date = date(today.year, max(1, ((index % 10) + 1)), 1)
            end_date = start_date + timedelta(days=365)
            status = LeaseStatus.ACTIVE if index < 7 else LeaseStatus.DRAFT
            lease, created = Lease.objects.get_or_create(
                landlord=landlord,
                property=properties[index],
                tenant=tenants[index],
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                    "rent_amount": properties[index].rent_default,
                    "security_deposit": properties[index].rent_default * Decimal("2.00"),
                    "payment_frequency": PaymentFrequency.MONTHLY if index % 3 else PaymentFrequency.QUARTERLY,
                    "due_day": min(5 + index, 15),
                    "grace_days": 2 + (index % 4),
                    "late_fee_type": LateFeeType.NONE,
                    "late_fee_value": Decimal("0.00"),
                    "status": status,
                    "notes": "Seeded lease for UI testing.",
                },
            )
            if created and lease.status == LeaseStatus.ACTIVE:
                generate_payment_schedule(lease)
            leases.append(lease)
        return leases

    def _create_payments(self, landlord, leases, count, rng):
        payments = []
        methods = list(PaymentMethod.values)
        active_leases = [lease for lease in leases if lease.status == LeaseStatus.ACTIVE]
        for index in range(count):
            lease = active_leases[index % len(active_leases)]
            amount = lease.rent_amount if index % 2 == 0 else (lease.rent_amount / Decimal("2.00"))
            reference = f"DEMO-PAY-{index + 1:03d}"
            if Payment.objects.filter(landlord=landlord, reference_number=reference).exists():
                payments.append(Payment.objects.get(landlord=landlord, reference_number=reference))
                continue

            payment = record_payment(
                landlord=landlord,
                created_by=landlord,
                lease=lease,
                tenant=lease.tenant,
                payment_date=lease.start_date + timedelta(days=3 + index),
                amount=amount,
                payment_method=methods[index % len(methods)],
                reference_number=reference,
                notes="Seeded payment for UI testing.",
                audit_note="Seed script",
            )
            payments.append(payment)
        return payments

    def _create_expenses(self, landlord, properties, count, rng):
        expenses = []
        categories = list(ExpenseCategory.values)
        methods = list(PaymentMethod.values)
        today = date.today()
        for index in range(count):
            expense, _ = Expense.objects.get_or_create(
                landlord=landlord,
                property=properties[index % len(properties)],
                expense_date=today - timedelta(days=index * 3),
                category=categories[index % len(categories)],
                defaults={
                    "amount": Decimal("1200.00") + (Decimal(index) * Decimal("350.00")),
                    "vendor_name": f"Demo Vendor {index + 1}",
                    "payment_method": methods[index % len(methods)],
                    "notes": "Seeded expense for UI testing.",
                },
            )
            expenses.append(expense)
        return expenses
