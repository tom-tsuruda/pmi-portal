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

    def filter_deals(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_status = str(filters.get("deal_status") or "").strip()
        deal_type = str(filters.get("deal_type") or "").strip().lower()
        region_main = str(filters.get("region_main") or "").strip().lower()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()
        show_archived = bool(filters.get("show_archived"))

        results = []

        for row in rows:
            row_status = str(row.get("deal_status") or "").strip()
            row_is_active = str(row.get("is_active") or "1").strip()

            # 通常は ARCHIVED と is_active=0 を非表示
            if not show_archived:
                if row_status == "ARCHIVED":
                    continue
                if row_is_active == "0":
                    continue

            if deal_status and row_status != deal_status:
                continue

            if deal_type:
                row_deal_type = str(row.get("deal_type") or "").lower()
                if deal_type not in row_deal_type:
                    continue

            if region_main:
                row_region = str(row.get("region_main") or "").lower()
                if region_main not in row_region:
                    continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if keyword:
                deal_id = str(row.get("deal_id") or "").lower()
                deal_name = str(row.get("deal_name") or "").lower()
                target_company_name = str(row.get("target_company_name") or "").lower()
                description = str(row.get("description") or "").lower()

                if (
                    keyword not in deal_id
                    and keyword not in deal_name
                    and keyword not in target_company_name
                    and keyword not in description
                ):
                    continue

            results.append(row)

        return results