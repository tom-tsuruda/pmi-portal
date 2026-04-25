from django.contrib import messages
from django.shortcuts import render

from apps.core.exceptions import RepositoryError
from apps.dashboard.services import DashboardService


dashboard_service = DashboardService()


def home(request):
    try:
        context = dashboard_service.get_dashboard_context()
    except RepositoryError as e:
        context = {
            "active_deal_count": 0,
            "incomplete_task_count": 0,
            "overdue_task_count": 0,
            "unresolved_raid_count": 0,
            "pending_approval_count": 0,
            "recent_logs": [],
            "upcoming_tasks": [],
            "recent_deals": [],
        }
        messages.error(request, str(e))

    return render(request, "dashboard/home.html", context)