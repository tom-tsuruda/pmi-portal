from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.dtos import DealCreateDTO
from apps.deals.forms import DealCreateForm
from apps.deals.services import DealService
from apps.tasks.services import TaskService
from apps.raid.services import RaidService
from apps.documents.services import DocumentService


deal_service = DealService()
task_service = TaskService()
raid_service = RaidService()
document_service = DocumentService()


def deal_list(request):
    try:
        deals = deal_service.list_deals()
    except RepositoryError as e:
        deals = []
        messages.error(request, str(e))

    return render(
        request,
        "deals/deal_list.html",
        {
            "deals": deals,
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
                return redirect("deals:list")
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

    task_total = len(tasks)
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
        },
    )