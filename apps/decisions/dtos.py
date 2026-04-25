from dataclasses import dataclass


@dataclass
class DecisionCreateDTO:
    deal_id: str
    phase_id: str
    workstream_id: str
    title: str
    summary: str = ""
    decision_detail: str = ""
    decision_type: str = "GENERAL"
    decided_by_user_id: str = ""
    decided_on: str = ""
    decision_meeting_name: str = ""
    related_task_id: str = ""
    related_raid_id: str = ""
    related_document_id: str = ""
    impact_summary: str = ""
    followup_action_required_flag: int = 0
    status: str = "DRAFT"