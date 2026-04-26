from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.kpis.dtos import KpiCreateDTO
from apps.kpis.forms import KpiCreateForm, KpiFilterForm
from apps.kpis.services import KpiService


kpi_service = KpiService()
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


def kpi_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = KpiFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        kpis = kpi_service.filter_kpis(filters)
    except RepositoryError as e:
        kpis = []
        messages.error(request, str(e))

    return render(
        request,
        "kpis/kpi_list.html",
        {
            "kpis": kpis,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def kpi_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = KpiCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            cleaned = form.cleaned_data.copy()

            if cleaned.get("measurement_date"):
                cleaned["measurement_date"] = cleaned["measurement_date"].strftime("%Y-%m-%d")
            else:
                cleaned["measurement_date"] = ""

            dto = KpiCreateDTO(**cleaned)

            try:
                kpi_id = kpi_service.create_kpi(dto)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="KPI",
                    object_id=kpi_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.kpi_name,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="KPIを登録しました。",
                )

                messages.success(request, f"KPIを登録しました: {kpi_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("kpis:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = KpiCreateForm(
            initial={"deal_id": initial_deal_id},
            deal_choices=deal_choices,
        )

    return render(
        request,
        "kpis/kpi_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )