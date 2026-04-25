from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.documents.dtos import DocumentUploadDTO
from apps.documents.forms import DocumentUploadForm
from apps.documents.services import DocumentService


document_service = DocumentService()


def document_list(request):
    deal_id = request.GET.get("deal_id") or ""

    try:
        documents = document_service.list_documents(deal_id=deal_id if deal_id else None)
    except RepositoryError as e:
        documents = []
        messages.error(request, str(e))

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
            "deal_id": deal_id,
        },
    )


def document_upload(request):
    initial_deal_id = request.GET.get("deal_id") or ""

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            uploaded_file = cleaned.pop("file")

            cleaned["is_template_flag"] = 1 if cleaned.get("is_template_flag") else 0
            cleaned["is_evidence_flag"] = 1 if cleaned.get("is_evidence_flag") else 0
            cleaned["is_report_flag"] = 1 if cleaned.get("is_report_flag") else 0

            dto = DocumentUploadDTO(**cleaned)

            try:
                document_id = document_service.upload_document(dto, uploaded_file)
                messages.success(request, f"資料を登録しました: {document_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("documents:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DocumentUploadForm(initial={"deal_id": initial_deal_id})

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )