from apps.dashboard.queries import dashboard_snapshot


def get_landlord_dashboard_summary(user):
    return dashboard_snapshot(user)
