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