from apps.core.base.repository import BaseExcelRepository


class ExcelSynergyRepository(BaseExcelRepository):
    sheet_name = "synergies"

    def get_last_synergy_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("synergy_id")
            for row in rows
            if row.get("synergy_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def find_one_by_synergy_id(self, synergy_id: str) -> dict | None:
        rows = self.find_all()

        for row in rows:
            if str(row.get("synergy_id") or "") == str(synergy_id):
                return row

        return None

    def filter_synergies(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        synergy_type = str(filters.get("synergy_type") or "").strip()
        status = str(filters.get("status") or "").strip()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()
        slippage_only = bool(filters.get("slippage_only"))

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if synergy_type and str(row.get("synergy_type") or "") != synergy_type:
                continue

            if status and str(row.get("status") or "") != status:
                continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if slippage_only and str(row.get("slippage_flag") or "0") != "1":
                continue

            if keyword:
                initiative_name = str(row.get("initiative_name") or "").lower()
                description = str(row.get("description") or "").lower()
                note = str(row.get("note") or "").lower()
                beginner_guidance = str(row.get("beginner_guidance") or "").lower()

                if (
                    keyword not in initiative_name
                    and keyword not in description
                    and keyword not in note
                    and keyword not in beginner_guidance
                ):
                    continue

            results.append(row)

        return results