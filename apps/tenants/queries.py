from apps.tenants.models import Tenant


def tenant_queryset_for_landlord(landlord):
    return Tenant.objects.filter(landlord=landlord)
