from apps.properties.models import Property


def create_property(*, landlord, **data):
    return Property.objects.create(landlord=landlord, **data)
