from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RepositoryError
from apps.deals.services import DealService
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.forms import TaskCreateForm, TaskFilterForm
from apps.tasks.services import TaskService


task_service = TaskService()
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


def task_list(request):
    deal_choices = _build_deal_choices(include_empty=True)
    filter_form = TaskFilterForm(request.GET or None, deal_choices=deal_choices)

    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    try:
        tasks = task_service.filter_tasks(filters)
    except RepositoryError as e:
        tasks = []
        messages.error(request, str(e))

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "filter_form": filter_form,
            "filters": filters,
        },
    )


def task_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = TaskCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = TaskCreateDTO(**form.cleaned_data)

            try:
                task_id = task_service.create_task(dto)

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="TASK",
                    object_id=task_id,
                    action_type="CREATE",
                    before_value="",
                    after_value=dto.title,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="タスクを登録しました。",
                )

                messages.success(request, f"タスクを登録しました: {task_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("tasks:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = TaskCreateForm(
            initial={"deal_id": initial_deal_id},
            deal_choices=deal_choices,
        )

    return render(
        request,
        "tasks/task_create.html",
        {
            "form": form,
            "deal_id": initial_deal_id,
        },
    )


def task_update_status(request, task_id: str):
    if request.method != "POST":
        return redirect("tasks:list")

    status = request.POST.get("status")
    deal_id = request.POST.get("deal_id") or ""

    if status not in ["TODO", "IN_PROGRESS", "DONE", "BLOCKED", "CANCELLED"]:
        messages.error(request, "不正なステータスです。")
        if deal_id:
            return redirect("deals:detail", deal_id=deal_id)
        return redirect("tasks:list")

    try:
        task_service.update_status(task_id, status)

        audit_service.log(
            deal_id=deal_id,
            object_type="TASK",
            object_id=task_id,
            action_type="STATUS_UPDATE",
            before_value="",
            after_value=status,
            acted_by_user_id="",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            note="タスクステータスを更新しました。",
        )

        messages.success(request, f"ステータスを更新しました: {task_id}")

    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("tasks:list")