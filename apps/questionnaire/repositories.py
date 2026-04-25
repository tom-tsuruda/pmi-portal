from apps.core.base.repository import BaseExcelRepository
from apps.core.constants import (
    SHEET_CHECKLIST_TEMPLATES,
    SHEET_QUESTIONNAIRE_ANSWERS,
    SHEET_QUESTIONNAIRE_QUESTIONS,
)


class ExcelQuestionRepository(BaseExcelRepository):
    sheet_name = SHEET_QUESTIONNAIRE_QUESTIONS

    def find_active(self) -> list[dict]:
        rows = self.find_all()
        active_rows = [
            row for row in rows
            if str(row.get("is_active", "1")) in ["1", "TRUE", "True", "true"]
        ]

        return sorted(
            active_rows,
            key=lambda row: int(row.get("display_order") or 9999),
        )


class ExcelQuestionnaireAnswerRepository(BaseExcelRepository):
    sheet_name = SHEET_QUESTIONNAIRE_ANSWERS

    def get_last_answer_id(self) -> str | None:
        rows = self.find_all()
        ids = [row.get("answer_id") for row in rows if row.get("answer_id")]
        return str(ids[-1]) if ids else None


class ExcelChecklistTemplateRepository(BaseExcelRepository):
    sheet_name = SHEET_CHECKLIST_TEMPLATES

    def find_active(self) -> list[dict]:
        rows = self.find_all()

        active_rows = [
            row for row in rows
            if str(row.get("is_active", "1")) in ["1", "TRUE", "True", "true"]
        ]

        return active_rows