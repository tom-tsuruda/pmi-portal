from django.contrib import messages
from django.shortcuts import redirect, render

from apps.approvals.dtos import ApprovalCreateDTO
from apps.approvals.forms import ApprovalCreateForm, ApprovalFilterForm
from apps.approvals.services import ApprovalService
from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService


approval_service = ApprovalService()
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


def approval_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = ApprovalFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        approvals = approval_service.filter_approvals(filters)
    except RepositoryError as e:
        approvals = []
        messages.error(request, str(e))

    return render(
        request,
        "approvals/approval_list.html",
        {
            "approvals": approvals,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def approval_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    initial_object_type = request.GET.get("object_type") or ""
    initial_object_id = request.GET.get("object_id") or ""

    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = ApprovalCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = ApprovalCreateDTO(**form.cleaned_data)

            try:
                approval_id = approval_service.create_approval(dto)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="APPROVAL",
                    object_id=approval_id,
                    action_type="CREATE",
                    before_value="",
                    after_value="REQUESTED",
                    acted_by_user_id=dto.requester_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note=f"承認依頼を登録しました。対象: {dto.object_type} / {dto.object_id}",
                )

                messages.success(request, f"承認依頼を登録しました: {approval_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("approvals:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = ApprovalCreateForm(
            initial={
                "deal_id": initial_deal_id,
                "object_type": initial_object_type,
                "object_id": initial_object_id,
            },
            deal_choices=deal_choices,
        )

    return render(
        request,
        "approvals/approval_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )


def approval_update_status(request, approval_id: str):
    if request.method != "POST":
        return redirect("approvals:list")

    approval_status = request.POST.get("approval_status")
    comment = request.POST.get("comment") or ""
    deal_id = request.POST.get("deal_id") or ""

    allowed_statuses = [
        "REQUESTED",
        "APPROVED",
        "REJECTED",
        "RETURNED",
        "CANCELLED",
    ]

    if approval_status not in allowed_statuses:
        messages.error(request, "不正な承認ステータスです。")
        if deal_id:
            return redirect("deals:detail", deal_id=deal_id)
        return redirect("approvals:list")

    try:
        approval_service.update_status(
            approval_id=approval_id,
            approval_status=approval_status,
            comment=comment,
        )

        audit_service.log(
            deal_id=deal_id,
            object_type="APPROVAL",
            object_id=approval_id,
            action_type="STATUS_UPDATE",
            before_value="",
            after_value=approval_status,
            acted_by_user_id="",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            note=f"承認ステータスを {approval_status} に更新しました。",
        )

        messages.success(request, f"承認ステータスを更新しました: {approval_id}")

    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("approvals:list")