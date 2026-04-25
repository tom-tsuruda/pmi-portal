from django.contrib import messages
from django.shortcuts import render

from apps.audit.forms import AuditLogFilterForm
from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError


audit_service = AuditLogService()


def audit_log_list(request):
    filter_form = AuditLogFilterForm(request.GET or None)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        logs = audit_service.filter_logs(filters)
    except RepositoryError as e:
        logs = []
        messages.error(request, str(e))

    return render(
        request,
        "audit/audit_log_list.html",
        {
            "logs": logs,
            "filter_form": filter_form,
            "filters": filters,
        },
    )