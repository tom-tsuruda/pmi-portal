from dataclasses import dataclass


@dataclass
class ApprovalCreateDTO:
    deal_id: str
    object_type: str
    object_id: str
    approval_step: str
    requester_user_id: str = ""
    approver_user_id: str = ""
    comment: str = ""