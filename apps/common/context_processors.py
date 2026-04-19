def navigation(_request):
    return {
        "navigation_items": [
            {"label": "Dashboard", "url": "dashboard:home"},
            {"label": "Properties", "url": "properties:list"},
            {"label": "Tenants", "url": "tenants:list"},
            {"label": "Leases", "url": "leases:list"},
            {"label": "Payments", "url": "payments:due_list"},
            {"label": "Expenses", "url": "expenses:list"},
        ]
    }
