from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.dtos import DealCreateDTO
from apps.deals.forms import DealCreateForm, DealFilterForm, DealStatusUpdateForm
from apps.deals.services import DealService
from apps.documents.services import DocumentService
from apps.raid.services import RaidService
from apps.tasks.services import TaskService
from apps.decisions.services import DecisionService
from apps.approvals.services import ApprovalService

deal_service = DealService()
task_service = TaskService()
raid_service = RaidService()
document_service = DocumentService()
decision_service = DecisionService()
approval_service = ApprovalService()

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
                messages.success(
                request,
                f"案件を登録しました: {deal_id}。続いて質問票に回答し、初期タスクを自動生成してください。"
                )
                return redirect("questionnaire:start", deal_id=deal_id)
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
        decisions = decision_service.list_decisions(deal_id=deal_id)
        tasks = task_service.list_tasks(deal_id=deal_id)
        raid_items = raid_service.list_items(deal_id=deal_id)
        documents = document_service.list_documents(deal_id=deal_id)
        approvals = approval_service.list_approvals(deal_id=deal_id)

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
            "decisions": decisions,
            "approvals": approvals,
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

from datetime import date, datetime

def deal_report(request, deal_id: str):
    try:
        deal = deal_service.get_deal(deal_id)
        tasks = task_service.list_tasks(deal_id=deal_id)
        raid_items = raid_service.list_items(deal_id=deal_id)
        documents = document_service.list_documents(deal_id=deal_id)
        decisions = decision_service.list_decisions(deal_id=deal_id)
        approvals = approval_service.list_approvals(deal_id=deal_id)

    except RecordNotFoundError:
        messages.error(request, f"案件が見つかりません: {deal_id}")
        return redirect("deals:list")

    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("deals:list")

    active_tasks = [
        task for task in tasks
        if str(task.get("status") or "") != "CANCELLED"
    ]

    completed_tasks = [
        task for task in active_tasks
        if str(task.get("status") or "") == "DONE"
    ]

    incomplete_tasks = [
        task for task in active_tasks
        if str(task.get("status") or "") not in ["DONE", "CANCELLED"]
    ]

    overdue_tasks = [
        task for task in incomplete_tasks
        if _is_overdue(task.get("due_date"))
    ]

    task_total = len(active_tasks)
    task_done = len(completed_tasks)
    task_progress = round((task_done / task_total) * 100) if task_total else 0

    unresolved_raid_items = [
        item for item in raid_items
        if str(item.get("status") or "") in ["OPEN", "IN_PROGRESS", "WATCH"]
    ]

    high_raid_items = [
        item for item in unresolved_raid_items
        if str(item.get("escalation_level") or "") in ["HIGH", "CRITICAL"]
    ]

    pending_approvals = [
        approval for approval in approvals
        if str(approval.get("approval_status") or "") == "REQUESTED"
    ]

    decided_decisions = [
        decision for decision in decisions
        if str(decision.get("status") or "") == "DECIDED"
    ]

    report_summary = {
        "task_total": task_total,
        "task_done": task_done,
        "task_progress": task_progress,
        "incomplete_task_count": len(incomplete_tasks),
        "overdue_task_count": len(overdue_tasks),
        "unresolved_raid_count": len(unresolved_raid_items),
        "high_raid_count": len(high_raid_items),
        "decision_count": len(decisions),
        "decided_decision_count": len(decided_decisions),
        "pending_approval_count": len(pending_approvals),
        "document_count": len(documents),
    }

    return render(
        request,
        "deals/deal_report.html",
        {
            "deal": deal,
            "tasks": tasks,
            "incomplete_tasks": incomplete_tasks,
            "overdue_tasks": overdue_tasks,
            "raid_items": raid_items,
            "unresolved_raid_items": unresolved_raid_items,
            "high_raid_items": high_raid_items,
            "documents": documents,
            "decisions": decisions,
            "approvals": approvals,
            "pending_approvals": pending_approvals,
            "report_summary": report_summary,
        },
    )


def _is_overdue(due_date_value) -> bool:
    due_date = _parse_date(due_date_value)

    if due_date is None:
        return False

    return due_date < date.today()


def _parse_date(value) -> date | None:
    if not value:
        return None

    text = str(value).strip()

    if not text:
        return None

    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None