from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.synergies.dtos import SynergyCreateDTO
from apps.synergies.forms import SynergyCreateForm, SynergyFilterForm
from apps.synergies.services import SynergyService


synergy_service = SynergyService()
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


def synergy_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = SynergyFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        synergies = synergy_service.filter_synergies(filters)
    except RepositoryError as e:
        synergies = []
        messages.error(request, str(e))

    return render(
        request,
        "synergies/synergy_list.html",
        {
            "synergies": synergies,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def synergy_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = SynergyCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            cleaned = form.cleaned_data.copy()

            cleaned["slippage_flag"] = 1 if cleaned.get("slippage_flag") else 0

            for key in [
                "planned_start_date",
                "planned_end_date",
                "actual_start_date",
                "actual_end_date",
            ]:
                if cleaned.get(key):
                    cleaned[key] = cleaned[key].strftime("%Y-%m-%d")
                else:
                    cleaned[key] = ""

            dto = SynergyCreateDTO(**cleaned)

            try:
                synergy_id = synergy_service.create_synergy(dto)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="SYNERGY",
                    object_id=synergy_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.initiative_name,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="Synergy施策を登録しました。",
                )

                messages.success(request, f"Synergy施策を登録しました: {synergy_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("synergies:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = SynergyCreateForm(
            initial={"deal_id": initial_deal_id},
            deal_choices=deal_choices,
        )

    return render(
        request,
        "synergies/synergy_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )