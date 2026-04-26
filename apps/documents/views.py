from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.documents.dtos import DocumentUploadDTO
from apps.documents.forms import (
    DocumentFilterForm,
    DocumentUploadForm,
    TemplateUploadForm,
)
from apps.documents.services import DocumentService
from apps.tasks.services import TaskService
from django.http import FileResponse
from urllib.parse import quote

document_service = DocumentService()
deal_service = DealService()
task_service = TaskService()
audit_service = AuditLogService()


def _build_deal_choices(include_empty: bool = False) -> list[tuple[str, str]]:
    choices = []

    if include_empty:
        choices.append(("", "すべて"))

    try:
        deals = deal_service.list_deals()
    except RepositoryError:
        deals = []

    for deal in deals:
        deal_id = deal.get("deal_id") or ""
        deal_name = deal.get("deal_name") or ""
        target_company_name = deal.get("target_company_name") or ""

        if not deal_id:
            continue

        label_parts = [deal_id]

        if deal_name:
            label_parts.append(deal_name)

        if target_company_name:
            label_parts.append(f"対象：{target_company_name}")

        choices.append((deal_id, " / ".join(label_parts)))

    if not choices:
        choices.append(("", "案件がありません。先に案件を登録してください。"))

    return choices


def _build_task_choices(deal_id: str | None = None) -> list[tuple[str, str]]:
    choices = [("", "関連タスクなし")]

    if not deal_id:
        return choices

    try:
        tasks = task_service.list_tasks(deal_id=deal_id)
    except RepositoryError:
        tasks = []

    for task in tasks:
        task_id = task.get("task_id") or ""
        title = task.get("title") or ""
        phase_id = task.get("phase_id") or ""
        workstream_id = task.get("workstream_id") or ""
        evidence_status = task.get("evidence_status") or ""

        if not task_id:
            continue

        label_parts = [task_id]

        if title:
            label_parts.append(title)

        if phase_id or workstream_id:
            label_parts.append(f"{phase_id}/{workstream_id}")

        label_parts.append(f"証跡: {evidence_status or '未添付'}")

        choices.append((task_id, " / ".join(label_parts)))

    return choices


def document_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = DocumentFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        documents = document_service.filter_documents(filters)
    except RepositoryError as e:
        documents = []
        messages.error(request, str(e))

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def template_library(request):
    """
    Template Library。
    documentsシートのうち is_template_flag=1 のものだけを表示する。
    """
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = DocumentFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {
        "template_only": True,
        "show_deleted": False,
    }

    if filter_form.is_valid():
        cleaned = filter_form.cleaned_data.copy()
        filters.update(cleaned)

    filters["template_only"] = True

    try:
        templates = document_service.filter_documents(filters)
    except RepositoryError as e:
        templates = []
        messages.error(request, str(e))

    return render(
        request,
        "documents/template_library.html",
        {
            "templates": templates,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def document_upload(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    initial_task_id = request.GET.get("task_id") or ""
    template_mode = request.GET.get("template") in ["1", "true", "True", "yes", "YES"]

    if template_mode:
        return _template_upload(request)

    return _normal_document_upload(
        request=request,
        initial_deal_id=initial_deal_id,
        initial_task_id=initial_task_id,
    )


def _template_upload(request):
    """
    テンプレート登録専用処理。
    画面には案件・担当・関連タスクを出さず、保存時に共通値を自動セットする。
    """
    if request.method == "POST":
        form = TemplateUploadForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            uploaded_file = cleaned.pop("file")

            dto = DocumentUploadDTO(
                deal_id="TEMPLATE_LIBRARY",
                phase_id=cleaned.get("phase_id") or "DAY1",
                workstream_id=cleaned.get("workstream_id") or "PMO",
                document_title=cleaned.get("document_title") or "",
                document_type="TEMPLATE",
                category=cleaned.get("category") or "Template Library",
                subcategory=cleaned.get("subcategory") or "",
                owner_user_id="",
                access_level=cleaned.get("access_level") or "INTERNAL",
                linked_task_id="",
                linked_raid_id="",
                tags=cleaned.get("tags") or "",
                document_purpose=cleaned.get("document_purpose") or "",
                is_template_flag=1,
                is_evidence_flag=0,
                is_report_flag=0,
            )

            try:
                document_id = document_service.upload_document(dto, uploaded_file)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="TEMPLATE",
                    object_id=document_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.document_title,
                    acted_by_user_id="",
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="テンプレートを登録しました。",
                )

                messages.success(request, f"テンプレートを登録しました: {document_id}")
                return redirect("documents:templates")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = TemplateUploadForm(
            initial={
                "access_level": "INTERNAL",
                "category": "Template Library",
            }
        )

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "deal_id": "",
            "template_mode": True,
        },
    )


def _normal_document_upload(request, initial_deal_id: str = "", initial_task_id: str = ""):
    """
    案件に紐づく通常資料・証跡アップロード処理。
    """
    deal_choices = _build_deal_choices(include_empty=False)

    selected_deal_id = initial_deal_id
    if request.method == "POST":
        selected_deal_id = request.POST.get("deal_id") or initial_deal_id

    task_choices = _build_task_choices(deal_id=selected_deal_id)

    if request.method == "POST":
        form = DocumentUploadForm(
            request.POST,
            request.FILES,
            deal_choices=deal_choices,
            task_choices=task_choices,
        )

        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            uploaded_file = cleaned.pop("file")

            cleaned["is_template_flag"] = 1 if cleaned.get("is_template_flag") else 0
            cleaned["is_evidence_flag"] = 1 if cleaned.get("is_evidence_flag") else 0
            cleaned["is_report_flag"] = 1 if cleaned.get("is_report_flag") else 0

            dto = DocumentUploadDTO(**cleaned)

            try:
                document_id = document_service.upload_document(dto, uploaded_file)

                if dto.linked_task_id and int(dto.is_evidence_flag or 0) == 1:
                    task_service.mark_evidence_attached(
                        task_id=dto.linked_task_id,
                        document_id=document_id,
                    )

                    audit_service.log(
                        deal_id=dto.deal_id,
                        object_type="TASK",
                        object_id=dto.linked_task_id,
                        action_type="EVIDENCE_ATTACHED",
                        before_value="REQUIRED",
                        after_value=document_id,
                        acted_by_user_id=dto.owner_user_id,
                        ip_address=request.META.get("REMOTE_ADDR", ""),
                        note="証跡文書のアップロードによりタスクの証跡状態を更新しました。",
                    )

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="DOCUMENT",
                    object_id=document_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.document_title,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="資料を登録しました。",
                )

                messages.success(request, f"資料を登録しました: {document_id}")

                if dto.linked_task_id and int(dto.is_evidence_flag or 0) == 1:
                    messages.success(
                        request,
                        f"関連タスク {dto.linked_task_id} の証跡状態を ATTACHED に更新しました。",
                    )

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("documents:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DocumentUploadForm(
            initial={
                "deal_id": initial_deal_id,
                "linked_task_id": initial_task_id,
                "document_type": "EVIDENCE",
                "is_evidence_flag": True,
            },
            deal_choices=deal_choices,
            task_choices=task_choices,
        )

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "deal_id": selected_deal_id,
            "template_mode": False,
        },
    )
def document_download(request, document_id: str):
    try:
        document = document_service.get_document(document_id)
        absolute_path = document_service.get_absolute_file_path(document_id)

    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("documents:list")

    except Exception as e:
        messages.error(request, str(e))
        return redirect("documents:list")

    file_name = document.get("file_name") or absolute_path.name

    response = FileResponse(
        open(absolute_path, "rb"),
        as_attachment=False,
        filename=file_name,
    )

    # 日本語ファイル名対策
    response["Content-Disposition"] = (
        f"inline; filename*=UTF-8''{quote(str(file_name))}"
    )

    return response

def document_delete(request, document_id: str):
    if request.method != "POST":
        return redirect("documents:list")

    deal_id = request.POST.get("deal_id") or ""
    return_to = request.POST.get("return_to") or ""

    try:
        document_service.soft_delete_document(document_id)

        audit_service.log(
            deal_id=deal_id,
            object_type="DOCUMENT",
            object_id=document_id,
            action_type="SOFT_DELETE",
            before_value="ACTIVE",
            after_value="DELETED",
            acted_by_user_id="",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            note="資料を削除済みにしました。",
        )

        messages.success(request, f"資料を削除済みにしました: {document_id}")

    except RepositoryError as e:
        messages.error(request, str(e))

    if return_to == "templates":
        return redirect("documents:templates")

    if deal_id and deal_id != "TEMPLATE_LIBRARY":
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("documents:list")