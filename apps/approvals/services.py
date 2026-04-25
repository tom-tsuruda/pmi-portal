from apps.approvals.dtos import ApprovalCreateDTO
from apps.approvals.repositories import ExcelApprovalRepository
from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id


class ApprovalService:
    def __init__(self, approval_repo: ExcelApprovalRepository | None = None):
        self.approval_repo = approval_repo or ExcelApprovalRepository()

    def list_approvals(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return self.approval_repo.find_by_deal(deal_id)

        return self.approval_repo.find_all()

    def filter_approvals(self, filters: dict) -> list[dict]:
        return self.approval_repo.filter_approvals(filters)

    def create_approval(self, dto: ApprovalCreateDTO) -> str:
        last_id = self.approval_repo.get_last_approval_id()
        approval_id = next_id("APP", last_id)

        current_time = now_str()

        record = {
            "approval_id": approval_id,
            "deal_id": dto.deal_id,
            "object_type": dto.object_type,
            "object_id": dto.object_id,
            "approval_step": dto.approval_step,
            "requester_user_id": dto.requester_user_id,
            "approver_user_id": dto.approver_user_id,
            "requested_at": current_time,
            "approved_at": "",
            "approval_status": "REQUESTED",
            "comment": dto.comment,
            "created_at": current_time,
        }

        self.approval_repo.append_row(record)
        return approval_id

    def update_status(self, approval_id: str, approval_status: str, comment: str = "") -> None:
        updates = {
            "approval_status": approval_status,
        }

        if approval_status == "APPROVED":
            updates["approved_at"] = now_str()

        if comment:
            updates["comment"] = comment

        self.approval_repo.update_row("approval_id", approval_id, updates)

