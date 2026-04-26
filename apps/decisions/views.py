from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.decisions.dtos import DecisionCreateDTO
from apps.decisions.forms import DecisionCreateForm, DecisionFilterForm
from apps.decisions.services import DecisionService


decision_service = DecisionService()
deal_service = DealService()


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


def decision_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = DecisionFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        decisions = decision_service.filter_decisions(filters)
    except RepositoryError as e:
        decisions = []
        messages.error(request, str(e))

    return render(
        request,
        "decisions/decision_list.html",
        {
            "decisions": decisions,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def decision_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    initial_task_id = request.GET.get("task_id") or ""
    initial_raid_id = request.GET.get("raid_id") or ""
    initial_document_id = request.GET.get("document_id") or ""

    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = DecisionCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            cleaned["followup_action_required_flag"] = (
                1 if cleaned.get("followup_action_required_flag") else 0
            )

            dto = DecisionCreateDTO(**cleaned)

            try:
                decision_id = decision_service.create_decision(dto)
                messages.success(request, f"意思決定を登録しました: {decision_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("decisions:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DecisionCreateForm(
            initial={
                "deal_id": initial_deal_id,
                "related_task_id": initial_task_id,
                "related_raid_id": initial_raid_id,
                "related_document_id": initial_document_id,
            },
            deal_choices=deal_choices,
        )

    return render(
        request,
        "decisions/decision_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )


def decision_update_status(request, decision_id: str):
    if request.method != "POST":
        return redirect("decisions:list")

    status = request.POST.get("status")
    deal_id = request.POST.get("deal_id") or ""

    if status not in ["DRAFT", "PROPOSED", "DECIDED", "SUPERSEDED", "CANCELLED"]:
        messages.error(request, "不正なステータスです。")
        if deal_id:
            return redirect("deals:detail", deal_id=deal_id)
        return redirect("decisions:list")

    try:
        decision_service.update_status(decision_id, status)
        messages.success(request, f"意思決定ステータスを更新しました: {decision_id}")
    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("decisions:list")