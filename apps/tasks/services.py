from apps.core.exceptions import RecordNotFoundError
from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.repositories import ExcelTaskRepository


class TaskService:
    def __init__(self, task_repo: ExcelTaskRepository | None = None):
        self.task_repo = task_repo or ExcelTaskRepository()

    def list_tasks(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            tasks = self.task_repo.find_by_deal(deal_id)
        else:
            tasks = self.task_repo.find_all()

        return self.enrich_dependency_status(tasks)

    def filter_tasks(self, filters: dict) -> list[dict]:
        tasks = self.task_repo.filter_tasks(filters)
        return self.enrich_dependency_status(tasks)

    def get_task(self, task_id: str) -> dict:
        if not task_id:
            raise RecordNotFoundError("tasks: task_id is empty")

        task = self.task_repo.find_one_by_task_id(task_id)

        if not task:
            raise RecordNotFoundError(f"tasks: task_id={task_id} not found")

        return task

    def create_task(self, dto: TaskCreateDTO) -> str:
        last_id = self.task_repo.get_last_task_id()
        task_id = next_id("TASK", last_id)

        current_time = now_str()

        record = {
            "task_id": task_id,
            "deal_id": dto.deal_id,
            "phase_id": dto.phase_id,
            "workstream_id": dto.workstream_id,
            "task_code": task_id,

            "title": dto.title,
            "description": dto.description,
            "task_type": "MANUAL" if not dto.template_source_id else "TEMPLATE",
            "priority": dto.priority,
            "status": "TODO",

            "owner_user_id": dto.owner_user_id,
            "approver_user_id": "",

            "start_date": "",
            "due_date": dto.due_date,
            "completed_date": "",

            "approval_required_flag": 0,

            "evidence_required_flag": 1,
            "evidence_status": "REQUIRED",

            "template_source_id": dto.template_source_id,
            "dependency_task_ids": dto.dependency_task_ids,
            "related_decision_id": "",
            "related_raid_id": "",
            "related_document_id": "",

            "regulation_flag": dto.regulation_flag,
            "critical_path_flag": 0,
            "overdue_flag": 0,

            "why_this_task": dto.why_this_task or "PMIの進捗を管理するための基本タスクです。",
            "beginner_guidance": dto.beginner_guidance or "まずは担当者・期限・完了条件を確認してください。",
            "completion_note": "",

            "created_by_user_id": dto.owner_user_id,
            "created_at": current_time,
            "updated_at": current_time,
            "sort_order": "",
        }

        self.task_repo.append_row(record)
        return task_id

    def create_task_if_not_exists_by_template(self, dto: TaskCreateDTO) -> tuple[bool, str | None]:
        if dto.template_source_id:
            exists = self.task_repo.exists_by_deal_and_template(
                deal_id=dto.deal_id,
                template_source_id=dto.template_source_id,
            )

            if exists:
                return False, None

        task_id = self.create_task(dto)
        return True, task_id

    def update_task(
        self,
        task_id: str,
        dto: TaskCreateDTO,
        status: str = "TODO",
        completion_note: str = "",
    ) -> None:
        task = self.get_task(task_id)

        updates = {
            "deal_id": dto.deal_id,
            "phase_id": dto.phase_id,
            "workstream_id": dto.workstream_id,
            "title": dto.title,
            "description": dto.description,
            "priority": dto.priority,
            "status": status,
            "owner_user_id": dto.owner_user_id,
            "due_date": dto.due_date,
            "template_source_id": dto.template_source_id,
            "dependency_task_ids": dto.dependency_task_ids,
            "regulation_flag": dto.regulation_flag,
            "why_this_task": dto.why_this_task or "PMIの進捗を管理するための基本タスクです。",
            "beginner_guidance": dto.beginner_guidance or "まずは担当者・期限・完了条件を確認してください。",
            "completion_note": completion_note,
            "updated_at": now_str(),
        }

        previous_status = str(task.get("status") or "")

        if status == "DONE" and previous_status != "DONE":
            updates["completed_date"] = now_str()
        elif status != "DONE":
            updates["completed_date"] = ""

        self.task_repo.update_row("task_id", task_id, updates)

    def update_status(self, task_id: str, status: str) -> None:
        updates = {
            "status": status,
            "updated_at": now_str(),
        }

        if status == "DONE":
            updates["completed_date"] = now_str()
        else:
            updates["completed_date"] = ""

        self.task_repo.update_row(
            "task_id",
            task_id,
            updates,
        )

    def mark_evidence_attached(self, task_id: str, document_id: str = "") -> None:
        if not task_id:
            return

        updates = {
            "evidence_status": "ATTACHED",
            "updated_at": now_str(),
        }

        if document_id:
            updates["related_document_id"] = document_id

        self.task_repo.update_row(
            "task_id",
            task_id,
            updates,
        )

    def parse_dependency_ids(self, value: str) -> list[str]:
        text = str(value or "").replace("、", ",").replace("，", ",")

        return [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]

    def get_predecessor_tasks(self, task: dict) -> list[dict]:
        dependency_ids = self.parse_dependency_ids(task.get("dependency_task_ids"))
        predecessors = []

        for dependency_id in dependency_ids:
            try:
                predecessors.append(self.get_task(dependency_id))
            except RecordNotFoundError:
                predecessors.append(
                    {
                        "task_id": dependency_id,
                        "title": "見つからないタスクID",
                        "status": "MISSING",
                    }
                )

        return predecessors

    def get_blocking_predecessor_tasks(self, task: dict) -> list[dict]:
        predecessors = self.get_predecessor_tasks(task)

        return [
            item for item in predecessors
            if str(item.get("status") or "") != "DONE"
        ]

    def is_blocked_by_dependencies(self, task: dict) -> bool:
        if str(task.get("status") or "") in ["DONE", "CANCELLED"]:
            return False

        return len(self.get_blocking_predecessor_tasks(task)) > 0

    def enrich_dependency_status(self, tasks: list[dict]) -> list[dict]:
        enriched_tasks = []

        for task in tasks:
            item = task.copy()
            dependency_ids = self.parse_dependency_ids(item.get("dependency_task_ids"))
            blocking_tasks = self.get_blocking_predecessor_tasks(item) if dependency_ids else []

            item["dependency_count"] = len(dependency_ids)
            item["blocking_dependency_count"] = len(blocking_tasks)
            item["dependency_status"] = "BLOCKED" if blocking_tasks else ("HAS_DEPENDENCY" if dependency_ids else "")
            item["is_dependency_blocked"] = bool(blocking_tasks)

            enriched_tasks.append(item)

        return enriched_tasks

    def list_blocked_tasks(self, deal_id: str | None = None) -> list[dict]:
        tasks = self.list_tasks(deal_id=deal_id)

        return [
            task for task in tasks
            if task.get("is_dependency_blocked")
        ]

    def list_dependent_tasks(self, task_id: str) -> list[dict]:
        tasks = self.list_tasks()
        dependents = []

        for task in tasks:
            dependency_ids = self.parse_dependency_ids(task.get("dependency_task_ids"))

            if task_id in dependency_ids:
                dependents.append(task)

        return dependents