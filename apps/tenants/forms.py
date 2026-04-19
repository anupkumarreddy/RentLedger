from apps.common.forms import BaseStyledForm
from apps.tenants.models import Tenant


class TenantForm(BaseStyledForm):
    class Meta:
        model = Tenant
        exclude = ["landlord", "created_at", "updated_at"]
