from apps.core.utils.datetime_utils import now_str, today_str
from apps.core.utils.ids import next_id
from apps.raid.dtos import RaidCreateDTO
from apps.raid.repositories import ExcelRaidRepository


class RaidService:
    def __init__(self, raid_repo: ExcelRaidRepository | None = None):
        self.raid_repo = raid_repo or ExcelRaidRepository()

    def list_items(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.raid_repo.find_by_deal(deal_id)

        return self.raid_repo.find_all()

    def filter_items(self, filters: dict) -> list[dict]:
        return self.raid_repo.filter_items(filters)

    def create_item(self, dto: RaidCreateDTO) -> str:
        last_id = self.raid_repo.get_last_raid_id()
        raid_id = next_id("RAID", last_id)

        probability = int(dto.probability)
        impact = int(dto.impact)
        score = probability * impact

        current_time = now_str()
        today = today_str()

        record = {
            "raid_id": raid_id,
            "deal_id": dto.deal_id,
            "raid_type": dto.raid_type,
            "phase_id": dto.phase_id,
            "workstream_id": dto.workstream_id,

            "title": dto.title,
            "description": dto.description,

            "probability": probability,
            "impact": impact,
            "score": score,

            "owner_user_id": dto.owner_user_id,
            "due_date": dto.due_date,

            "mitigation_plan": dto.mitigation_plan,
            "trigger_condition": dto.trigger_condition,

            "status": "OPEN",
            "escalation_level": self._decide_escalation_level(score),

            "related_task_id": "",
            "related_decision_id": "",
            "evidence_document_id": "",

            "why_it_matters": "PMIでは、リスク・課題・前提・依存関係を早めに見える化することで、統合失敗を防ぎます。",
            "beginner_guidance": "発生可能性と影響度を1〜5で入力してください。スコアが高いものから優先的に対応します。",

            "opened_date": today,
            "closed_date": "",
            "created_at": current_time,
            "updated_at": current_time,
        }

        self.raid_repo.append_row(record)
        return raid_id

    def update_status(self, raid_id: str, status: str) -> None:
        updates = {
            "status": status,
            "updated_at": now_str(),
        }

        if status == "CLOSED":
            updates["closed_date"] = today_str()

        self.raid_repo.update_row("raid_id", raid_id, updates)

    def _decide_escalation_level(self, score: int) -> str:
        if score >= 20:
            return "CRITICAL"
        if score >= 12:
            return "HIGH"
        if score >= 6:
            return "MEDIUM"
        return "LOW"