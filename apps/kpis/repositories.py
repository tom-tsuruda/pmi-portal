from apps.core.base.repository import BaseExcelRepository


class ExcelKpiRepository(BaseExcelRepository):
    sheet_name = "kpis"

    def get_last_kpi_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("kpi_id")
            for row in rows
            if row.get("kpi_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def filter_kpis(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        phase_id = str(filters.get("phase_id") or "").strip()
        kpi_category = str(filters.get("kpi_category") or "").strip()
        measurement_frequency = str(filters.get("measurement_frequency") or "").strip()
        status_color = str(filters.get("status_color") or "").strip()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()

        results = []

        for row in rows:
            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if phase_id and str(row.get("phase_id") or "") != phase_id:
                continue

            if kpi_category and str(row.get("kpi_category") or "") != kpi_category:
                continue

            if measurement_frequency and str(row.get("measurement_frequency") or "") != measurement_frequency:
                continue

            if status_color and str(row.get("status_color") or "") != status_color:
                continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if keyword:
                kpi_name = str(row.get("kpi_name") or "").lower()
                definition = str(row.get("definition") or "").lower()
                note = str(row.get("note") or "").lower()
                beginner_guidance = str(row.get("beginner_guidance") or "").lower()

                if (
                    keyword not in kpi_name
                    and keyword not in definition
                    and keyword not in note
                    and keyword not in beginner_guidance
                ):
                    continue

            results.append(row)

        return results