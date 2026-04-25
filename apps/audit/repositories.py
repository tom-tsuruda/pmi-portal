from apps.core.base.repository import BaseExcelRepository
from apps.core.constants import SHEET_AUDIT_LOGS


class ExcelAuditLogRepository(BaseExcelRepository):
    sheet_name = SHEET_AUDIT_LOGS

    def get_last_audit_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("audit_id")
            for row in rows
            if row.get("audit_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def filter_logs(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        object_type = str(filters.get("object_type") or "").strip()
        object_id = str(filters.get("object_id") or "").strip()
        action_type = str(filters.get("action_type") or "").strip()
        acted_by_user_id = str(filters.get("acted_by_user_id") or "").strip()

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if object_type and str(row.get("object_type") or "") != object_type:
                continue

            if object_id and str(row.get("object_id") or "") != object_id:
                continue

            if action_type and str(row.get("action_type") or "") != action_type:
                continue

            if acted_by_user_id and str(row.get("acted_by_user_id") or "") != acted_by_user_id:
                continue

            if keyword:
                audit_id = str(row.get("audit_id") or "").lower()
                before_value = str(row.get("before_value") or "").lower()
                after_value = str(row.get("after_value") or "").lower()
                note = str(row.get("note") or "").lower()

                if (
                    keyword not in audit_id
                    and keyword not in before_value
                    and keyword not in after_value
                    and keyword not in note
                ):
                    continue

            results.append(row)

        # 新しいものを上に表示したいので逆順
        return list(reversed(results))
        