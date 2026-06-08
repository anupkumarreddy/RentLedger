from apps.properties.models import Property


def create_property(*, landlord, **data):
    property_obj = Property(landlord=landlord, **data)
    property_obj.full_clean()
    property_obj.save()
    return property_obj
