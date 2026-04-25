from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.repositories import ExcelTaskRepository


class TaskService:
    def __init__(self, task_repo: ExcelTaskRepository | None = None):
        self.task_repo = task_repo or ExcelTaskRepository()

    def list_tasks(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.task_repo.find_by_deal(deal_id)

        return self.task_repo.find_all()

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
            "task_type": "MANUAL",
            "priority": dto.priority,
            "status": "TODO",

            "owner_user_id": dto.owner_user_id,
            "approver_user_id": "",

            "start_date": "",
            "due_date": dto.due_date,
            "completed_date": "",

            "approval_required_flag": 0,
            "evidence_required_flag": 0,
            "evidence_status": "NOT_REQUIRED",

            "template_source_id": "",
            "related_decision_id": "",
            "related_raid_id": "",
            "related_document_id": "",

            "regulation_flag": 0,
            "critical_path_flag": 0,
            "overdue_flag": 0,

            "why_this_task": "PMIの進捗を管理するための基本タスクです。",
            "beginner_guidance": "まずは担当者・期限・完了条件を確認してください。",
            "completion_note": "",

            "created_by_user_id": dto.owner_user_id,
            "created_at": current_time,
            "updated_at": current_time,
            "sort_order": "",
        }

        self.task_repo.append_row(record)
        return task_id

    def update_status(self, task_id: str, status: str) -> None:
        self.task_repo.update_row(
            "task_id",
            task_id,
            {
                "status": status,
                "updated_at": now_str(),
            },
        )