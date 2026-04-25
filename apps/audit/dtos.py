from dataclasses import dataclass


@dataclass
class AuditLogCreateDTO:
    deal_id: str
    object_type: str
    object_id: str
    action_type: str
    before_value: str = ""
    after_value: str = ""
    acted_by_user_id: str = ""
    ip_address: str = ""
    note: str = ""