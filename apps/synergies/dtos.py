from dataclasses import dataclass


@dataclass
class SynergyCreateDTO:
    deal_id: str
    workstream_id: str
    synergy_type: str
    initiative_name: str
    description: str = ""
    baseline_amount: float = 0
    target_amount: float = 0
    actual_amount: float = 0
    one_time_cost_amount: float = 0
    run_rate_amount: float = 0
    confidence_percent: float = 0
    planned_start_date: str = ""
    planned_end_date: str = ""
    actual_start_date: str = ""
    actual_end_date: str = ""
    owner_user_id: str = ""
    status: str = "PLANNED"
    slippage_flag: int = 0
    note: str = ""
    beginner_guidance: str = ""