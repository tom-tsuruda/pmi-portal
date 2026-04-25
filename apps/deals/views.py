from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.dtos import DealCreateDTO
from apps.deals.forms import DealCreateForm, DealFilterForm, DealStatusUpdateForm
from apps.deals.services import DealService
from apps.documents.services import DocumentService
from apps.raid.services import RaidService
from apps.tasks.services import TaskService


deal_service = DealService()
task_service = TaskService()
raid_service = RaidService()
document_service = DocumentService()


def deal_list(request):
    filter_form = DealFilterForm(request.GET or None)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        deals = deal_service.filter_deals(filters)
    except RepositoryError as e:
        deals = []
        messages.error(request, str(e))

    return render(
        request,
        "deals/deal_list.html",
        {
            "deals": deals,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def deal_create(request):
    if request.method == "POST":
        form = DealCreateForm(request.POST)

        if form.is_valid():
            dto = DealCreateDTO(**form.cleaned_data)

            try:
                deal_id = deal_service.create_deal(dto)
                messages.success(request, f"案件を登録しました: {deal_id}")
                return redirect("deals:detail", deal_id=deal_id)
            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DealCreateForm()

    return render(
        request,
        "deals/deal_create.html",
        {
            "form": form,
        },
    )


def deal_detail(request, deal_id: str):
    try:
        deal = deal_service.get_deal(deal_id)
        tasks = task_service.list_tasks(deal_id=deal_id)
        raid_items = raid_service.list_items(deal_id=deal_id)
        documents = document_service.list_documents(deal_id=deal_id)

    except RecordNotFoundError:
        messages.error(request, f"案件が見つかりません: {deal_id}")
        return redirect("deals:list")

    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("deals:list")

    task_total = len([task for task in tasks if task.get("status") != "CANCELLED"])
    task_done = len([task for task in tasks if task.get("status") == "DONE"])
    task_progress = round((task_done / task_total) * 100) if task_total else 0

    open_raid_count = len(
        [
            item
            for item in raid_items
            if item.get("status") in ["OPEN", "IN_PROGRESS", "WATCH"]
        ]
    )

    high_raid_count = len(
        [
            item
            for item in raid_items
            if item.get("escalation_level") in ["HIGH", "CRITICAL"]
        ]
    )

    status_form = DealStatusUpdateForm(
        initial={"deal_status": deal.get("deal_status") or "DRAFT"}
    )

    return render(
        request,
        "deals/deal_detail.html",
        {
            "deal": deal,
            "tasks": tasks,
            "raid_items": raid_items,
            "documents": documents,
            "task_total": task_total,
            "task_done": task_done,
            "task_progress": task_progress,
            "open_raid_count": open_raid_count,
            "high_raid_count": high_raid_count,
            "status_form": status_form,
        },
    )


def deal_update_status(request, deal_id: str):
    if request.method != "POST":
        return redirect("deals:detail", deal_id=deal_id)

    form = DealStatusUpdateForm(request.POST)

    if form.is_valid():
        deal_status = form.cleaned_data["deal_status"]

        try:
            deal_service.update_status(deal_id, deal_status)
            messages.success(request, f"案件ステータスを更新しました: {deal_status}")
        except RepositoryError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "不正な案件ステータスです。")

    return redirect("deals:detail", deal_id=deal_id)


def deal_archive(request, deal_id: str):
    if request.method != "POST":
        return redirect("deals:detail", deal_id=deal_id)

    try:
        deal_service.archive_deal(deal_id)
        messages.success(request, f"案件をアーカイブしました: {deal_id}")
    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("deals:list")


def deal_reactivate(request, deal_id: str):
    if request.method != "POST":
        return redirect("deals:detail", deal_id=deal_id)

    try:
        deal_service.reactivate_deal(deal_id)
        messages.success(request, f"案件を再開しました: {deal_id}")
    except RepositoryError as e:
        messages.error(request, str(e))

    return redirect("deals:detail", deal_id=deal_id)