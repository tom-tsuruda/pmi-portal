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

    def find_one_by_task_id(self, task_id: str) -> dict | None:
        rows = self.find_all()

        for row in rows:
            if str(row.get("task_id") or "") == str(task_id):
                return row

        return None

    def exists_by_deal_and_template(self, deal_id: str, template_source_id: str) -> bool:
        if not deal_id or not template_source_id:
            return False

        rows = self.find_all()

        for row in rows:
            same_deal = str(row.get("deal_id", "")) == str(deal_id)
            same_template = str(row.get("template_source_id", "")) == str(template_source_id)

            if same_deal and same_template:
                return True

        return False

    def filter_tasks(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        status = str(filters.get("status") or "").strip()
        priority = str(filters.get("priority") or "").strip()
        phase_id = str(filters.get("phase_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()

        show_cancelled = bool(filters.get("show_cancelled"))

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if status and str(row.get("status") or "") != status:
                continue

            if priority and str(row.get("priority") or "") != priority:
                continue

            if phase_id and str(row.get("phase_id") or "") != phase_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if not show_cancelled and str(row.get("status") or "") == "CANCELLED":
                continue

            if keyword:
                title = str(row.get("title") or "").lower()
                description = str(row.get("description") or "").lower()
                why_this_task = str(row.get("why_this_task") or "").lower()

                if (
                    keyword not in title
                    and keyword not in description
                    and keyword not in why_this_task
                ):
                    continue

            results.append(row)

        return results