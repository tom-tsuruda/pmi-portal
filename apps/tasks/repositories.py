from apps.core.base.repository import BaseExcelRepository


class ExcelTaskRepository(BaseExcelRepository):
    sheet_name = "tasks"

    def get_last_task_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("task_id")
            for row in rows
            if row.get("task_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)