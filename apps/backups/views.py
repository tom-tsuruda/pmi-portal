from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.backups.services import BackupService
from apps.core.exceptions import RepositoryError


backup_service = BackupService()
audit_service = AuditLogService()


def backup_home(request):
    try:
        backup_info = backup_service.get_backup_info()
    except RepositoryError as e:
        backup_info = None
        messages.error(request, str(e))

    return render(
        request,
        "backups/backup_home.html",
        {
            "backup_info": backup_info,
        },
    )


def backup_create(request):
    if request.method != "POST":
        return redirect("backups:home")

    try:
        backup_info = backup_service.create_backup()

        audit_service.log(
            deal_id="",
            object_type="BACKUP",
            object_id="master_data_backup.xlsx",
            action_type="BACKUP_CREATE",
            before_value="",
            after_value=backup_info.get("backup_path", ""),
            acted_by_user_id="",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            note="Excel台帳のバックアップを作成しました。",
        )

        messages.success(request, "Excel台帳のバックアップを作成しました。")

    except RepositoryError as e:
        messages.error(request, str(e))

    return redirect("backups:home")


def backup_download(request):
    try:
        backup_path = backup_service.get_download_path()
    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("backups:home")

    response = FileResponse(
        open(backup_path, "rb"),
        as_attachment=True,
        filename=backup_path.name,
    )

    return response