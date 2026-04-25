from dataclasses import dataclass


@dataclass
class TaskCreateDTO:
    deal_id: str
    phase_id: str
    workstream_id: str
    title: str
    description: str = ""
    priority: str = "MEDIUM"
    owner_user_id: str = ""
    due_date: str = ""