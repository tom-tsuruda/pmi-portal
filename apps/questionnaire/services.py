from datetime import timedelta

from django.utils import timezone

from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.deals.services import DealService
from apps.questionnaire.repositories import (
    ExcelChecklistTemplateRepository,
    ExcelQuestionRepository,
    ExcelQuestionnaireAnswerRepository,
)
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.services import TaskService


class QuestionnaireService:
    def __init__(
        self,
        question_repo: ExcelQuestionRepository | None = None,
        answer_repo: ExcelQuestionnaireAnswerRepository | None = None,
        template_repo: ExcelChecklistTemplateRepository | None = None,
        task_service: TaskService | None = None,
        deal_service: DealService | None = None,
    ):
        self.question_repo = question_repo or ExcelQuestionRepository()
        self.answer_repo = answer_repo or ExcelQuestionnaireAnswerRepository()
        self.template_repo = template_repo or ExcelChecklistTemplateRepository()
        self.task_service = task_service or TaskService()
        self.deal_service = deal_service or DealService()

    def list_questions(self) -> list[dict]:
        return self.question_repo.find_active()

    def save_answers(self, deal_id: str, questions: list[dict], cleaned_data: dict) -> int:
        count = 0
        current_time = now_str()
        last_id = self.answer_repo.get_last_answer_id()

        for question in questions:
            question_id = question.get("question_id")
            question_code = question.get("question_code")
            field_name = f"question_{question_id}"
            answer_value = cleaned_data.get(field_name, "")

            last_id = next_id("ANS", last_id)

            record = {
                "answer_id": last_id,
                "deal_id": deal_id,
                "question_id": question_id,
                "question_code": question_code,
                "answer_value": answer_value,
                "created_at": current_time,
                "updated_at": current_time,
            }

            self.answer_repo.append_row(record)
            count += 1

        return count

    def generate_tasks_from_templates(self, deal_id: str) -> int:
        deal = self.deal_service.get_deal(deal_id)
        templates = self.template_repo.find_active()

        generated_count = 0

        for template in templates:
            task_title = template.get("task_title")
            if not task_title:
                continue

            due_date = self._build_due_date(template.get("default_due_offset_days"))

            dto = TaskCreateDTO(
                deal_id=deal_id,
                phase_id=template.get("phase_id") or "DAY1",
                workstream_id=template.get("workstream_id") or "PMO",
                title=task_title,
                description=template.get("task_description") or "",
                priority=template.get("default_priority") or "MEDIUM",
                owner_user_id=deal.get("owner_user_id") or "u001",
                due_date=due_date,
            )

            self.task_service.create_task(dto)
            generated_count += 1

        return generated_count

    def _build_due_date(self, offset_days) -> str:
        try:
            days = int(offset_days or 0)
        except ValueError:
            days = 0

        target_date = timezone.localdate() + timedelta(days=days)
        return target_date.strftime("%Y-%m-%d")