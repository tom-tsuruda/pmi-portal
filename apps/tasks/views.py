from django.contrib import messages
from django.shortcuts import redirect, render

from apps.audit.services import AuditLogService
from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.services import DealService
from apps.documents.services import DocumentService
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.forms import TaskCreateForm, TaskEditForm, TaskFilterForm
from apps.tasks.services import TaskService


task_service = TaskService()
deal_service = DealService()
document_service = DocumentService()
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


def _task_initial(task: dict) -> dict:
    initial = task.copy()
    initial["regulation_flag"] = str(initial.get("regulation_flag") or "0") == "1"
    return initial


def _task_dto_from_cleaned(cleaned: dict) -> TaskCreateDTO:
    return TaskCreateDTO(
        deal_id=cleaned.get("deal_id") or "",
        phase_id=cleaned.get("phase_id") or "",
        workstream_id=cleaned.get("workstream_id") or "",
        title=cleaned.get("title") or "",
        description=cleaned.get("description") or "",
        priority=cleaned.get("priority") or "MEDIUM",
        owner_user_id=cleaned.get("owner_user_id") or "",
        due_date=cleaned.get("due_date") or "",
        template_source_id=cleaned.get("template_source_id") or "",
        regulation_flag=1 if cleaned.get("regulation_flag") else 0,
        why_this_task=cleaned.get("why_this_task") or "",
        beginner_guidance=cleaned.get("beginner_guidance") or "",
    )


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


def task_related_templates(request, task_id: str):
    try:
        task = task_service.get_task(task_id)

        templates = document_service.list_templates()
        related_templates = document_service.find_related_templates_for_task(
            task=task,
            templates=templates,
            limit=20,
        )

    except RecordNotFoundError:
        messages.error(request, f"タスクが見つかりません: {task_id}")
        return redirect("tasks:list")

    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("tasks:list")

    return render(
        request,
        "tasks/task_related_templates.html",
        {
            "task": task,
            "related_templates": related_templates,
        },
    )


def task_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""
    deal_choices = _build_deal_choices(include_empty=False)

    if request.method == "POST":
        form = TaskCreateForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = _task_dto_from_cleaned(form.cleaned_data)

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


def task_edit(request, task_id: str):
    deal_choices = _build_deal_choices(include_empty=False)

    try:
        task = task_service.get_task(task_id)
    except RecordNotFoundError:
        messages.error(request, f"タスクが見つかりません: {task_id}")
        return redirect("tasks:list")
    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("tasks:list")

    if request.method == "POST":
        form = TaskEditForm(request.POST, deal_choices=deal_choices)

        if form.is_valid():
            dto = _task_dto_from_cleaned(form.cleaned_data)
            status = form.cleaned_data.get("status") or "TODO"
            completion_note = form.cleaned_data.get("completion_note") or ""

            try:
                task_service.update_task(
                    task_id=task_id,
                    dto=dto,
                    status=status,
                    completion_note=completion_note,
                )

                audit_service.log(
                    deal_id=dto.deal_id,
                    object_type="TASK",
                    object_id=task_id,
                    action_type="UPDATE",
                    before_value=str(task.get("status") or ""),
                    after_value=status,
                    acted_by_user_id=dto.owner_user_id,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    note="タスクを更新しました。",
                )

                messages.success(request, f"タスクを更新しました: {task_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("tasks:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = TaskEditForm(
            initial=_task_initial(task),
            deal_choices=deal_choices,
        )

    return render(
        request,
        "tasks/task_edit.html",
        {
            "form": form,
            "task": task,
            "task_id": task_id,
            "deal_id": task.get("deal_id") or "",
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