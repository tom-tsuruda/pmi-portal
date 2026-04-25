from apps.core.base.repository import BaseExcelRepository
from apps.core.constants import SHEET_DECISIONS


class ExcelDecisionRepository(BaseExcelRepository):
    sheet_name = SHEET_DECISIONS

    def get_last_decision_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("decision_id")
            for row in rows
            if row.get("decision_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def filter_decisions(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        phase_id = str(filters.get("phase_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        decision_type = str(filters.get("decision_type") or "").strip()
        status = str(filters.get("status") or "").strip()
        decided_by_user_id = str(filters.get("decided_by_user_id") or "").strip()

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if phase_id and str(row.get("phase_id") or "") != phase_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if decision_type and str(row.get("decision_type") or "") != decision_type:
                continue

            if status and str(row.get("status") or "") != status:
                continue

            if decided_by_user_id and str(row.get("decided_by_user_id") or "") != decided_by_user_id:
                continue

            if keyword:
                title = str(row.get("title") or "").lower()
                summary = str(row.get("summary") or "").lower()
                decision_detail = str(row.get("decision_detail") or "").lower()
                impact_summary = str(row.get("impact_summary") or "").lower()
                meeting_name = str(row.get("decision_meeting_name") or "").lower()

                if (
                    keyword not in title
                    and keyword not in summary
                    and keyword not in decision_detail
                    and keyword not in impact_summary
                    and keyword not in meeting_name
                ):
                    continue

            results.append(row)

        return results