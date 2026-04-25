from apps.core.utils.datetime_utils import now_str, today_str
from apps.core.utils.ids import next_id
from apps.decisions.dtos import DecisionCreateDTO
from apps.decisions.repositories import ExcelDecisionRepository


class DecisionService:
    def __init__(self, decision_repo: ExcelDecisionRepository | None = None):
        self.decision_repo = decision_repo or ExcelDecisionRepository()

    def list_decisions(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.decision_repo.find_by_deal(deal_id)

        return self.decision_repo.find_all()

    def filter_decisions(self, filters: dict) -> list[dict]:
        return self.decision_repo.filter_decisions(filters)

    def create_decision(self, dto: DecisionCreateDTO) -> str:
        last_id = self.decision_repo.get_last_decision_id()
        decision_id = next_id("DEC", last_id)

        current_time = now_str()

        record = {
            "decision_id": decision_id,
            "deal_id": dto.deal_id,
            "phase_id": dto.phase_id,
            "workstream_id": dto.workstream_id,

            "decision_code": decision_id,
            "title": dto.title,
            "summary": dto.summary,
            "decision_detail": dto.decision_detail,
            "decision_type": dto.decision_type,

            "decided_by_user_id": dto.decided_by_user_id,
            "decided_on": dto.decided_on or today_str(),
            "decision_meeting_name": dto.decision_meeting_name,

            "related_task_id": dto.related_task_id,
            "related_raid_id": dto.related_raid_id,
            "related_document_id": dto.related_document_id,

            "impact_summary": dto.impact_summary,
            "followup_action_required_flag": dto.followup_action_required_flag,
            "status": dto.status,

            "beginner_guidance": "この記録は、PMIにおける重要な意思決定の履歴です。誰が、いつ、何を決めたかを後から確認できるように残します。",

            "created_at": current_time,
            "updated_at": current_time,
        }

        self.decision_repo.append_row(record)
        return decision_id

    def update_status(self, decision_id: str, status: str) -> None:
        self.decision_repo.update_row(
            "decision_id",
            decision_id,
            {
                "status": status,
                "updated_at": now_str(),
            },
        )