from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.forms import TaskCreateForm
from apps.tasks.services import TaskService


task_service = TaskService()


def task_list(request):
    deal_id = request.GET.get("deal_id") or ""

    try:
        tasks = task_service.list_tasks(deal_id=deal_id if deal_id else None)
    except RepositoryError as e:
        tasks = []
        messages.error(request, str(e))

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "deal_id": deal_id,
        },
    )


def task_create(request):
    initial_deal_id = request.GET.get("deal_id") or ""

    if request.method == "POST":
        form = TaskCreateForm(request.POST)

        if form.is_valid():
            dto = TaskCreateDTO(**form.cleaned_data)

            try:
                task_id = task_service.create_task(dto)
                messages.success(request, f"タスクを登録しました: {task_id}")

                if dto.deal_id:
                    return redirect("deals:detail", deal_id=dto.deal_id)

                return redirect("tasks:list")

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = TaskCreateForm(initial={"deal_id": initial_deal_id})

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

    if status not in ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"]:
        messages.error(request, "不正なステータスです。")
        if deal_id:
            return redirect("deals:detail", deal_id=deal_id)
        return redirect("tasks:list")

    try:
        task_service.update_status(task_id, status)
        messages.success(request, f"ステータスを更新しました: {task_id}")
    except RepositoryError as e:
        messages.error(request, str(e))

    if deal_id:
        return redirect("deals:detail", deal_id=deal_id)

    return redirect("tasks:list")