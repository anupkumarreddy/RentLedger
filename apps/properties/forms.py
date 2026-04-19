from apps.common.forms import BaseStyledForm
from apps.properties.models import Property


class PropertyForm(BaseStyledForm):
    class Meta:
        model = Property
        exclude = ["landlord", "created_at", "updated_at"]
