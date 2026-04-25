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

    def generate_tasks_from_templates(
        self,
        deal_id: str,
        questions: list[dict] | None = None,
        cleaned_data: dict | None = None,
    ) -> dict:
        """
        checklist_templates をもとにタスクを生成する。

        条件分岐仕様:
        - trigger_question_code が空なら常に生成対象
        - trigger_question_code がある場合、
          質問票の回答が trigger_answer_value と一致したときだけ生成
        - 同じ deal_id + template_source_id のタスクは重複生成しない
        """

        deal = self.deal_service.get_deal(deal_id)
        templates = self.template_repo.find_active()

        answer_map = self._build_answer_map(
            questions=questions or [],
            cleaned_data=cleaned_data or {},
        )

        created_count = 0
        skipped_count = 0
        condition_skipped_count = 0

        for template in templates:
            task_title = template.get("task_title")
            template_code = template.get("template_code")

            if not task_title:
                continue

            if not self._template_matches_answers(template, answer_map):
                condition_skipped_count += 1
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
                template_source_id=template_code or "",
                evidence_required_flag=self._to_int_flag(
                    template.get("evidence_required_flag")
                ),
                regulation_flag=self._to_int_flag(
                    template.get("regulation_flag")
                ),
                why_this_task=template.get("why_this_task") or "",
                beginner_guidance=template.get("beginner_guidance") or "",
            )

            created, _task_id = self.task_service.create_task_if_not_exists_by_template(dto)

            if created:
                created_count += 1
            else:
                skipped_count += 1

        return {
            "created_count": created_count,
            "skipped_count": skipped_count,
            "condition_skipped_count": condition_skipped_count,
        }

    def _build_answer_map(self, questions: list[dict], cleaned_data: dict) -> dict:
        """
        cleaned_data を question_code ベースの辞書に変換する。

        例:
        {
            "EMPLOYEE_EXISTS": "YES",
            "TSA_EXISTS": "NO",
        }
        """

        answer_map = {}

        for question in questions:
            question_id = question.get("question_id")
            question_code = question.get("question_code")

            if not question_code:
                continue

            field_name = f"question_{question_id}"
            value = cleaned_data.get(field_name, "")

            answer_map[str(question_code).strip()] = self._normalize_answer(value)

        return answer_map

    def _template_matches_answers(self, template: dict, answer_map: dict) -> bool:
        """
        テンプレートの条件が質問票回答に合うか判定する。

        checklist_templates 側の想定列:
        - trigger_question_code
        - trigger_answer_value

        trigger_question_code が空なら、条件なしとして常に True。
        """

        trigger_question_code = str(
            template.get("trigger_question_code") or ""
        ).strip()

        trigger_answer_value = str(
            template.get("trigger_answer_value") or ""
        ).strip()

        if not trigger_question_code:
            return True

        expected_answer = self._normalize_answer(trigger_answer_value or "YES")
        actual_answer = answer_map.get(trigger_question_code)

        if actual_answer is None:
            return False

        return actual_answer == expected_answer

    def _normalize_answer(self, value) -> str:
        """
        回答値を比較しやすい形にそろえる。
        YES/NO、True/False、1/0 などを吸収する。
        """

        text = str(value or "").strip()

        upper_text = text.upper()

        if upper_text in ["YES", "Y", "TRUE", "1", "はい", "有", "あり"]:
            return "YES"

        if upper_text in ["NO", "N", "FALSE", "0", "いいえ", "無", "なし"]:
            return "NO"

        return text

    def _build_due_date(self, offset_days) -> str:
        try:
            days = int(offset_days or 0)
        except ValueError:
            days = 0

        target_date = timezone.localdate() + timedelta(days=days)
        return target_date.strftime("%Y-%m-%d")

    def _to_int_flag(self, value) -> int:
        if str(value).strip() in ["1", "TRUE", "True", "true", "YES", "Yes", "yes"]:
            return 1

        return 0