from django import template
from django.utils.http import urlencode


register = template.Library()


@register.filter
def currency(value):
    if value is None:
        return "-"
    try:
        return f"Rs. {value:,.2f}"
    except (TypeError, ValueError):
        return value


@register.filter
def currency_compact(value):
    """Short currency form for tight KPI spots: Rs. 1.2L / Rs. 3.4Cr."""
    if value is None:
        return "-"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_00_00_000:
        return f"{sign}Rs. {value / 1_00_00_000:.2f}Cr"
    if value >= 1_00_000:
        return f"{sign}Rs. {value / 1_00_000:.2f}L"
    if value >= 1_000:
        return f"{sign}Rs. {value / 1_000:.1f}K"
    return f"{sign}Rs. {value:,.0f}"


# Maps a status / occupancy value to a badge colour class.
BADGE_CLASSES = {
    # Lease status
    "draft": "badge-slate",
    "active": "badge-emerald",
    "completed": "badge-sky",
    "terminated": "badge-rose",
    "cancelled": "badge-slate",
    # Installment status
    "paid": "badge-emerald",
    "partial": "badge-amber",
    "unpaid": "badge-slate",
    "overdue": "badge-rose",
    # Occupancy helpers
    "occupied": "badge-emerald",
    "vacant": "badge-amber",
}


@register.filter
def split(value, separator=","):
    if not value:
        return []
    return [item.strip() for item in str(value).split(separator)]


@register.filter
def badge_class(value):
    if value is None:
        return "badge-slate"
    return BADGE_CLASSES.get(str(value).lower(), "badge-slate")


@register.filter
def percent_of(part, whole):
    """Return an integer percentage (0-100) of part/whole, clamped."""
    try:
        part = float(part or 0)
        whole = float(whole or 0)
    except (TypeError, ValueError):
        return 0
    if whole <= 0:
        return 0
    return max(0, min(100, round(part / whole * 100)))


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Rebuild the current querystring, overriding the given params.

    Used by pagination/filter links so they preserve existing filters.
    """
    request = context.get("request")
    params = request.GET.copy() if request else {}
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params)
