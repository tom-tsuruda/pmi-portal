from dataclasses import dataclass


@dataclass
class KpiCreateDTO:
    deal_id: str
    workstream_id: str
    phase_id: str
    kpi_name: str
    kpi_category: str
    definition: str = ""
    unit: str = ""
    baseline_value: float = 0
    target_value: float = 0
    actual_value: float = 0
    measurement_frequency: str = "MONTHLY"
    measurement_date: str = ""
    owner_user_id: str = ""
    threshold_red: float = 0
    threshold_yellow: float = 0
    threshold_green: float = 0
    status_color: str = "GREEN"
    note: str = ""
    beginner_guidance: str = ""