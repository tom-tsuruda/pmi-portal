from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.kpis.dtos import KpiCreateDTO
from apps.kpis.repositories import ExcelKpiRepository


class KpiService:
    def __init__(self, kpi_repo: ExcelKpiRepository | None = None):
        self.kpi_repo = kpi_repo or ExcelKpiRepository()

    def list_kpis(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.kpi_repo.find_by_deal(deal_id)

        return self.kpi_repo.find_all()

    def filter_kpis(self, filters: dict) -> list[dict]:
        return self.kpi_repo.filter_kpis(filters)

    def create_kpi(self, dto: KpiCreateDTO) -> str:
        last_id = self.kpi_repo.get_last_kpi_id()
        kpi_id = next_id("KPI", last_id)

        current_time = now_str()

        record = {
            "kpi_id": kpi_id,
            "deal_id": dto.deal_id,
            "workstream_id": dto.workstream_id,
            "phase_id": dto.phase_id,
            "kpi_name": dto.kpi_name,
            "kpi_category": dto.kpi_category,
            "definition": dto.definition,
            "unit": dto.unit,

            "baseline_value": dto.baseline_value,
            "target_value": dto.target_value,
            "actual_value": dto.actual_value,

            "measurement_frequency": dto.measurement_frequency,
            "measurement_date": dto.measurement_date,
            "owner_user_id": dto.owner_user_id,

            "threshold_red": dto.threshold_red,
            "threshold_yellow": dto.threshold_yellow,
            "threshold_green": dto.threshold_green,
            "status_color": dto.status_color,

            "note": dto.note,
            "beginner_guidance": dto.beginner_guidance
            or "このKPIは、PMIの進捗・効果・リスク状態を定量的に確認するための指標です。",

            "created_at": current_time,
            "updated_at": current_time,
        }

        self.kpi_repo.append_row(record)
        return kpi_id

    def build_summary(self, deal_id: str) -> dict:
        kpis = self.list_kpis(deal_id=deal_id)

        green_count = 0
        yellow_count = 0
        red_count = 0
        blank_count = 0

        for item in kpis:
            color = str(item.get("status_color") or "").strip().upper()

            if color == "GREEN":
                green_count += 1
            elif color == "YELLOW":
                yellow_count += 1
            elif color == "RED":
                red_count += 1
            else:
                blank_count += 1

        total = len(kpis)

        return {
            "count": total,
            "green_count": green_count,
            "yellow_count": yellow_count,
            "red_count": red_count,
            "blank_count": blank_count,
            "attention_count": yellow_count + red_count,
            "healthy_rate": round((green_count / total) * 100) if total else 0,
        }