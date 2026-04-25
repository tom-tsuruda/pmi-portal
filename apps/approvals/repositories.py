from apps.core.base.repository import BaseExcelRepository
from apps.core.constants import SHEET_APPROVALS


class ExcelApprovalRepository(BaseExcelRepository):
    sheet_name = SHEET_APPROVALS

    def get_last_approval_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("approval_id")
            for row in rows
            if row.get("approval_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def filter_approvals(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        deal_id = str(filters.get("deal_id") or "").strip()
        object_type = str(filters.get("object_type") or "").strip()
        object_id = str(filters.get("object_id") or "").strip()
        approval_status = str(filters.get("approval_status") or "").strip()
        requester_user_id = str(filters.get("requester_user_id") or "").strip()
        approver_user_id = str(filters.get("approver_user_id") or "").strip()
        keyword = str(filters.get("keyword") or "").strip().lower()

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if object_type and str(row.get("object_type") or "") != object_type:
                continue

            if object_id and str(row.get("object_id") or "") != object_id:
                continue

            if approval_status and str(row.get("approval_status") or "") != approval_status:
                continue

            if requester_user_id and str(row.get("requester_user_id") or "") != requester_user_id:
                continue

            if approver_user_id and str(row.get("approver_user_id") or "") != approver_user_id:
                continue

            if keyword:
                approval_id = str(row.get("approval_id") or "").lower()
                approval_step = str(row.get("approval_step") or "").lower()
                comment = str(row.get("comment") or "").lower()

                if (
                    keyword not in approval_id
                    and keyword not in approval_step
                    and keyword not in comment
                ):
                    continue

            results.append(row)

        return results
        