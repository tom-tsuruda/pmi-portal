from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.raid.dtos import RaidCreateDTO
from apps.raid.forms import RaidCreateForm, RaidFilterForm
from apps.raid.services import RaidService


raid_service = RaidService()
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


def raid_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = RaidFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        items = raid_service.filter_items(filters)
    except RepositoryError as e:
        items = []
        messages.error(request, str(e))

    return render(
        request,
        "raid/raid_list.html",
        {
            "items": items,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def raid_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = RaidCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = RaidCreateDTO(**form.cleaned_data)

            try:
                raid_id = raid_service.create_item(dto)
                messages.success(request, f"RAID項目を登録しました: {raid_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("raid:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = RaidCreateForm(
            initial={"deal_id": initial_deal_id},
            deal_choices=deal_choices,
        )

    return render(
        request,
        "raid/raid_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )


def raid_update_status(request, raid_id: str):
    if request.method != "POST":
        return redirect("raid:list")

    status = request.POST.get("status")
    deal_id = request.POST.get("deal_id") or ""

    if status not in ["OPEN", "IN_PROGRESS", "WATCH", "CLOSED"]:
        messages.error(request, "不正なステータスです。")
        if deal_id:
            return redirect("deals:detail", deal_id=deal_id)
        return redirect("raid:list")

    try:
        raid_service.update_status(raid_id, status)
        messages.success(request, f"ステータスを更新しました: {raid_id}")
    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("raid:list")