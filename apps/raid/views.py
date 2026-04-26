from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.services import DealService
from apps.raid.dtos import RaidCreateDTO
from apps.raid.forms import RaidCreateForm, RaidEditForm, RaidFilterForm
from apps.raid.services import RaidService


raid_service = RaidService()
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


def _raid_dto_from_cleaned(cleaned: dict) -> RaidCreateDTO:
    return RaidCreateDTO(
        deal_id=cleaned.get("deal_id") or "",
        raid_type=cleaned.get("raid_type") or "",
        phase_id=cleaned.get("phase_id") or "",
        workstream_id=cleaned.get("workstream_id") or "",
        title=cleaned.get("title") or "",
        description=cleaned.get("description") or "",
        probability=int(cleaned.get("probability") or 1),
        impact=int(cleaned.get("impact") or 1),
        owner_user_id=cleaned.get("owner_user_id") or "",
        due_date=cleaned.get("due_date") or "",
        mitigation_plan=cleaned.get("mitigation_plan") or "",
        trigger_condition=cleaned.get("trigger_condition") or "",
    )


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
            dto = _raid_dto_from_cleaned(form.cleaned_data)

            try:
                raid_id = raid_service.create_item(dto)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="RAID",
                    object_id=raid_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.title,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="RAID項目を登録しました。",
                )

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

def raid_detail(request, raid_id: str):
    try:
        item = raid_service.get_item(raid_id)

    except RecordNotFoundError:
        messages.error(request, f"RAID項目が見つかりません: {raid_id}")
        return redirect("raid:list")

    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("raid:list")

    return render(
        request,
        "raid/raid_detail.html",
        {
            "item": item,
            "raid_id": raid_id,
        },
    )

def raid_edit(request, raid_id: str):
    deal_choices = _build_deal_choices(include_empty=False)

    try:
        item = raid_service.get_item(raid_id)
    except RecordNotFoundError:
        messages.error(request, f"RAID項目が見つかりません: {raid_id}")
        return redirect("raid:list")
    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("raid:list")

    if request.method == "POST":
        form = RaidEditForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = _raid_dto_from_cleaned(form.cleaned_data)
            status = form.cleaned_data.get("status") or "OPEN"

            try:
                raid_service.update_item(
                    raid_id=raid_id,
                    dto=dto,
                    status=status,
                )

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="RAID",
                    object_id=raid_id,
                    action_type="UPDATE",
                    before_value=str(item.get("status") or ""),
                    after_value=status,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="RAID項目を更新しました。",
                )

                messages.success(request, f"RAID項目を更新しました: {raid_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("raid:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = RaidEditForm(
            initial=item,
            deal_choices=deal_choices,
        )

    return render(
        request,
        "raid/raid_edit.html",
        {
            "form": form,
            "item": item,
            "raid_id": raid_id,
            "deal_id": item.get("deal_id") or "",
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

        audit_service.log(
            deal_id=deal_id,
            object_type="RAID",
            object_id=raid_id,
            action_type="STATUS_UPDATE",
            before_value="",
            after_value=status,
            acted_by_user_id="",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            note="RAIDステータスを更新しました。",
        )

        messages.success(request, f"ステータスを更新しました: {raid_id}")
    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("raid:list")