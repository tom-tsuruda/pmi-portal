from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.raid.dtos import RaidCreateDTO
from apps.raid.forms import RaidCreateForm, RaidFilterForm
from apps.raid.services import RaidService


raid_service = RaidService()


def raid_list(request):
    filter_form = RaidFilterForm(request.GET or None)

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

    if request.method == "POST":
        form = RaidCreateForm(request.POST)

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
        form = RaidCreateForm(initial={"deal_id": initial_deal_id})

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