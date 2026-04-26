from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.documents.dtos import DocumentUploadDTO
from apps.documents.forms import DocumentFilterForm, DocumentUploadForm
from apps.documents.services import DocumentService


document_service = DocumentService()
deal_service = DealService()
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


def document_upload(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = DocumentUploadForm(
            request.POST,
            request.FILES,
            deal_choices=deal_choices,
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

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("documents:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DocumentUploadForm(
            initial={"deal_id": initial_deal_id},
            deal_choices=deal_choices,
        )

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )


def document_delete(request, document_id: str):
    if request.method != "POST":
        return redirect("documents:list")

    deal_id = request.POST.get("deal_id") or ""

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

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("documents:list")