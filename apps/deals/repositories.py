from apps.core.base.repository import BaseExcelRepository
from apps.core.constants import SHEET_DEALS


class ExcelDealRepository(BaseExcelRepository):
    sheet_name = SHEET_DEALS

    def get_last_deal_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("deal_id")
            for row in rows
            if row.get("deal_id")
        ]

        if not ids:
            return None

        return str(ids[-1])