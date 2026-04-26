from datetime import date, datetime

from django.contrib import messages
from django.shortcuts import redirect, render

from apps.approvals.services import ApprovalService
from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.deals.dtos import DealCreateDTO
from apps.deals.forms import DealCreateForm, DealFilterForm, DealStatusUpdateForm
from apps.deals.services import DealService
from apps.decisions.services import DecisionService
from apps.documents.services import DocumentService
from apps.questionnaire.forms import QuestionnaireAnswerForm
from apps.questionnaire.services import QuestionnaireService
from apps.raid.services import RaidService
from apps.tasks.services import TaskService
from apps.synergies.services import SynergyService

deal_service = DealService()
task_service = TaskService()
raid_service = RaidService()
document_service = DocumentService()
decision_service = DecisionService()
approval_service = ApprovalService()
questionnaire_service = QuestionnaireService()
synergy_service = SynergyService()

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
    """
    新規案件登録。

    案件基本情報とPMI質問票を同じ画面で入力し、
    登録後に質問票回答を保存して初期タスクを自動生成する。
    """
    try:
        questions = questionnaire_service.list_questions()
    except RepositoryError as e:
        questions = []
        messages.error(request, str(e))

    if request.method == "POST":
        form = DealCreateForm(request.POST)
        questionnaire_form = QuestionnaireAnswerForm(
            request.POST,
            questions=questions,
        )

        if form.is_valid() and questionnaire_form.is_valid():
            dto = DealCreateDTO(**form.cleaned_data)

            try:
                deal_id = deal_service.create_deal(dto)

                answer_count = questionnaire_service.save_answers(
                    deal_id=deal_id,
                    questions=questions,
                    cleaned_data=questionnaire_form.cleaned_data,
                )

                result = questionnaire_service.generate_tasks_from_templates(
                    deal_id=deal_id,
                    questions=questions,
                    cleaned_data=questionnaire_form.cleaned_data,
                )

                messages.success(
                    request,
                    f"案件を登録しました: {deal_id}。"
                    f"質問票 {answer_count} 件を保存し、"
                    f"新規タスク {result['created_count']} 件を生成しました。"
                    f"既存タスク {result['skipped_count']} 件、"
                    f"条件不一致 {result['condition_skipped_count']} 件です。",
                )

                return redirect("deals:detail", deal_id=deal_id)

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = DealCreateForm()
        questionnaire_form = QuestionnaireAnswerForm(questions=questions)

    return render(
        request,
        "deals/deal_create.html",
        {
            "form": form,
            "questionnaire_form": questionnaire_form,
            "questions": questions,
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

    active_tasks = [
        task for task in tasks
        if str(task.get("status") or "") != "CANCELLED"
    ]

    completed_tasks = [
        task for task in active_tasks
        if str(task.get("status") or "") == "DONE"
    ]

    task_total = len(active_tasks)
    task_done = len(completed_tasks)
    task_progress = round((task_done / task_total) * 100) if task_total else 0

    phase_summary = _build_task_group_summary(
        tasks=tasks,
        group_key="phase_id",
        default_label="未設定",
    )

    workstream_summary = _build_task_group_summary(
        tasks=tasks,
        group_key="workstream_id",
        default_label="未設定",
    )

    evidence_summary = _build_evidence_summary(tasks)
    synergy_summary = synergy_service.build_summary(deal_id)

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
            "phase_summary": phase_summary,
            "workstream_summary": workstream_summary,
            "evidence_summary": evidence_summary,
            
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

    missing_evidence_tasks = _build_missing_evidence_tasks(tasks)

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
        "missing_evidence_count": len(missing_evidence_tasks),
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
            "missing_evidence_tasks": missing_evidence_tasks,
            "raid_items": raid_items,
            "unresolved_raid_items": unresolved_raid_items,
            "high_raid_items": high_raid_items,
            "documents": documents,
            "decisions": decisions,
            "approvals": approvals,
            "pending_approvals": pending_approvals,
            "report_summary": report_summary,
            "synergy_summary": synergy_summary,
        },
    )


def _build_task_group_summary(
    tasks: list[dict],
    group_key: str,
    default_label: str = "未設定",
) -> list[dict]:
    """
    タスクを phase_id / workstream_id などで集計する。
    CANCELLED は集計対象外。
    """
    grouped = {}

    for task in tasks:
        status = str(task.get("status") or "").strip()

        if status == "CANCELLED":
            continue

        key = str(task.get(group_key) or "").strip() or default_label

        if key not in grouped:
            grouped[key] = {
                "key": key,
                "label": key,
                "total": 0,
                "done": 0,
                "open": 0,
                "progress": 0,
                "high": 0,
                "overdue": 0,
            }

        grouped[key]["total"] += 1

        if status == "DONE":
            grouped[key]["done"] += 1
        else:
            grouped[key]["open"] += 1

        if str(task.get("priority") or "").strip() == "HIGH":
            grouped[key]["high"] += 1

        if _is_overdue(task.get("due_date")) and status not in ["DONE", "CANCELLED"]:
            grouped[key]["overdue"] += 1

    results = []

    for item in grouped.values():
        total = item["total"]
        done = item["done"]
        item["progress"] = round((done / total) * 100) if total else 0
        results.append(item)

    def sort_key(item):
        order = {
            "PRE_CLOSE": 10,
            "DAY1": 20,
            "DAY30": 30,
            "DAY100": 40,
            "TSA": 50,
            "POST100": 60,
            "PMO": 10,
            "HR": 20,
            "IT": 30,
            "FINANCE": 40,
            "LEGAL": 50,
            "SALES": 60,
            "OPS": 70,
            "COMMS": 80,
            "未設定": 999,
        }
        return order.get(item["key"], 500)

    return sorted(results, key=sort_key)


def _build_evidence_summary(tasks: list[dict]) -> dict:
    """
    全タスクを証跡対象として集計する。
    CANCELLED は対象外。
    """
    total = 0
    attached = 0
    missing = 0

    for task in tasks:
        status = str(task.get("status") or "").strip()

        if status == "CANCELLED":
            continue

        total += 1

        if _is_evidence_attached(task.get("evidence_status")):
            attached += 1
        else:
            missing += 1

    progress = round((attached / total) * 100) if total else 0

    return {
        "total": total,
        "attached": attached,
        "missing": missing,
        "progress": progress,
    }


def _build_missing_evidence_tasks(tasks: list[dict]) -> list[dict]:
    """
    レポート用。
    全タスクを証跡対象として、証跡未添付タスクを抽出する。
    CANCELLED は対象外。
    """
    missing_tasks = []

    for task in tasks:
        status = str(task.get("status") or "").strip()

        if status == "CANCELLED":
            continue

        if _is_evidence_attached(task.get("evidence_status")):
            continue

        missing_tasks.append(task)

    def sort_key(task):
        priority_order = {
            "HIGH": 10,
            "MEDIUM": 20,
            "LOW": 30,
        }

        phase_order = {
            "PRE_CLOSE": 10,
            "DAY1": 20,
            "DAY30": 30,
            "DAY100": 40,
            "TSA": 50,
            "POST100": 60,
        }

        priority = str(task.get("priority") or "")
        phase = str(task.get("phase_id") or "")
        due_date = str(task.get("due_date") or "9999-12-31")

        return (
            priority_order.get(priority, 99),
            phase_order.get(phase, 99),
            due_date,
            str(task.get("task_id") or ""),
        )

    return sorted(missing_tasks, key=sort_key)


def _is_evidence_attached(value) -> bool:
    text = str(value or "").strip()

    return text in {
        "ATTACHED",
        "COMPLETED",
        "DONE",
        "OK",
        "添付済",
        "完了",
    }


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