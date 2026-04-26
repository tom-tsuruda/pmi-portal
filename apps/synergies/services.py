from apps.core.exceptions import RecordNotFoundError
from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.synergies.dtos import SynergyCreateDTO
from apps.synergies.repositories import ExcelSynergyRepository


class SynergyService:
    def __init__(self, synergy_repo: ExcelSynergyRepository | None = None):
        self.synergy_repo = synergy_repo or ExcelSynergyRepository()

    def list_synergies(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.synergy_repo.find_by_deal(deal_id)

        return self.synergy_repo.find_all()

    def filter_synergies(self, filters: dict) -> list[dict]:
        return self.synergy_repo.filter_synergies(filters)

    def get_synergy(self, synergy_id: str) -> dict:
        synergy = self.synergy_repo.find_one_by_synergy_id(synergy_id)

        if not synergy:
            raise RecordNotFoundError(f"synergies: synergy_id={synergy_id} not found")

        return synergy

    def create_synergy(self, dto: SynergyCreateDTO) -> str:
        last_id = self.synergy_repo.get_last_synergy_id()
        synergy_id = next_id("SYN", last_id)

        current_time = now_str()

        record = {
            "synergy_id": synergy_id,
            "deal_id": dto.deal_id,
            "workstream_id": dto.workstream_id,
            "synergy_type": dto.synergy_type,
            "initiative_name": dto.initiative_name,
            "description": dto.description,

            "baseline_amount": dto.baseline_amount,
            "target_amount": dto.target_amount,
            "actual_amount": dto.actual_amount,
            "one_time_cost_amount": dto.one_time_cost_amount,
            "run_rate_amount": dto.run_rate_amount,
            "confidence_percent": dto.confidence_percent,

            "planned_start_date": dto.planned_start_date,
            "planned_end_date": dto.planned_end_date,
            "actual_start_date": dto.actual_start_date,
            "actual_end_date": dto.actual_end_date,

            "owner_user_id": dto.owner_user_id,
            "status": dto.status,
            "slippage_flag": dto.slippage_flag,
            "note": dto.note,
            "beginner_guidance": dto.beginner_guidance
            or "この施策は、PMIで期待する統合効果を金額・進捗・確度で管理するためのものです。",

            "created_at": current_time,
            "updated_at": current_time,
        }

        self.synergy_repo.append_row(record)
        return synergy_id

    def update_synergy(self, synergy_id: str, dto: SynergyCreateDTO) -> None:
        self.get_synergy(synergy_id)

        updates = {
            "deal_id": dto.deal_id,
            "workstream_id": dto.workstream_id,
            "synergy_type": dto.synergy_type,
            "initiative_name": dto.initiative_name,
            "description": dto.description,

            "baseline_amount": dto.baseline_amount,
            "target_amount": dto.target_amount,
            "actual_amount": dto.actual_amount,
            "one_time_cost_amount": dto.one_time_cost_amount,
            "run_rate_amount": dto.run_rate_amount,
            "confidence_percent": dto.confidence_percent,

            "planned_start_date": dto.planned_start_date,
            "planned_end_date": dto.planned_end_date,
            "actual_start_date": dto.actual_start_date,
            "actual_end_date": dto.actual_end_date,

            "owner_user_id": dto.owner_user_id,
            "status": dto.status,
            "slippage_flag": dto.slippage_flag,
            "note": dto.note,
            "beginner_guidance": dto.beginner_guidance
            or "この施策は、PMIで期待する統合効果を金額・進捗・確度で管理するためのものです。",

            "updated_at": now_str(),
        }

        self.synergy_repo.update_row("synergy_id", synergy_id, updates)

    def build_summary(self, deal_id: str) -> dict:
        synergies = self.list_synergies(deal_id=deal_id)

        target_amount = 0.0
        actual_amount = 0.0
        baseline_amount = 0.0
        one_time_cost_amount = 0.0
        run_rate_amount = 0.0
        slippage_count = 0
        at_risk_count = 0
        achieved_count = 0

        for item in synergies:
            target_amount += self._to_float(item.get("target_amount"))
            actual_amount += self._to_float(item.get("actual_amount"))
            baseline_amount += self._to_float(item.get("baseline_amount"))
            one_time_cost_amount += self._to_float(item.get("one_time_cost_amount"))
            run_rate_amount += self._to_float(item.get("run_rate_amount"))

            if str(item.get("slippage_flag") or "0") == "1":
                slippage_count += 1

            status = str(item.get("status") or "").strip()

            if status == "AT_RISK":
                at_risk_count += 1

            if status == "ACHIEVED":
                achieved_count += 1

        achievement_rate = round((actual_amount / target_amount) * 100) if target_amount else 0

        return {
            "count": len(synergies),
            "target_amount": target_amount,
            "actual_amount": actual_amount,
            "baseline_amount": baseline_amount,
            "one_time_cost_amount": one_time_cost_amount,
            "run_rate_amount": run_rate_amount,
            "achievement_rate": achievement_rate,
            "slippage_count": slippage_count,
            "at_risk_count": at_risk_count,
            "achieved_count": achieved_count,
        }

    def _to_float(self, value) -> float:
        if value is None:
            return 0.0

        text = str(value).replace(",", "").strip()

        if not text:
            return 0.0

        try:
            return float(text)
        except ValueError:
            return 0.0