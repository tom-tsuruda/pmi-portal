from apps.core.base.repository import BaseExcelRepository


class ExcelRaidRepository(BaseExcelRepository):
    sheet_name = "raid"

    def get_last_raid_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("raid_id")
            for row in rows
            if row.get("raid_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def find_one_by_raid_id(self, raid_id: str) -> dict | None:
        rows = self.find_all()

        for row in rows:
            if str(row.get("raid_id") or "") == str(raid_id):
                return row

        return None

    def filter_items(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        raid_type = str(filters.get("raid_type") or "").strip()
        status = str(filters.get("status") or "").strip()
        phase_id = str(filters.get("phase_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        escalation_level = str(filters.get("escalation_level") or "").strip()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()

        show_closed = bool(filters.get("show_closed"))

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if raid_type and str(row.get("raid_type") or "") != raid_type:
                continue

            if status and str(row.get("status") or "") != status:
                continue

            if phase_id and str(row.get("phase_id") or "") != phase_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if escalation_level and str(row.get("escalation_level") or "") != escalation_level:
                continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if not show_closed and str(row.get("status") or "") == "CLOSED":
                continue

            if keyword:
                title = str(row.get("title") or "").lower()
                description = str(row.get("description") or "").lower()
                mitigation_plan = str(row.get("mitigation_plan") or "").lower()
                trigger_condition = str(row.get("trigger_condition") or "").lower()
                why_it_matters = str(row.get("why_it_matters") or "").lower()

                if (
                    keyword not in title
                    and keyword not in description
                    and keyword not in mitigation_plan
                    and keyword not in trigger_condition
                    and keyword not in why_it_matters
                ):
                    continue

            results.append(row)

        return results