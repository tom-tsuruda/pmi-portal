from dataclasses import dataclass


@dataclass
class RaidCreateDTO:
    deal_id: str
    raid_type: str
    phase_id: str
    workstream_id: str
    title: str
    description: str = ""
    probability: int = 1
    impact: int = 1
    owner_user_id: str = ""
    due_date: str = ""
    mitigation_plan: str = ""
    trigger_condition: str = ""