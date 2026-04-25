from apps.audit.dtos import AuditLogCreateDTO
from apps.audit.repositories import ExcelAuditLogRepository
from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id


class AuditLogService:
    def __init__(self, audit_repo: ExcelAuditLogRepository | None = None):
        self.audit_repo = audit_repo or ExcelAuditLogRepository()

    def list_logs(self, deal_id: str | None = None) -> list[dict]:
        if deal_id:
            return list(reversed(self.audit_repo.find_by_deal(deal_id)))

        return list(reversed(self.audit_repo.find_all()))

    def filter_logs(self, filters: dict) -> list[dict]:
        return self.audit_repo.filter_logs(filters)

    def create_log(self, dto: AuditLogCreateDTO) -> str:
        last_id = self.audit_repo.get_last_audit_id()
        audit_id = next_id("AUDIT", last_id)

        record = {
            "audit_id": audit_id,
            "deal_id": dto.deal_id,
            "object_type": dto.object_type,
            "object_id": dto.object_id,
            "action_type": dto.action_type,
            "before_value": dto.before_value,
            "after_value": dto.after_value,
            "acted_by_user_id": dto.acted_by_user_id,
            "acted_at": now_str(),
            "ip_address": dto.ip_address,
            "note": dto.note,
        }

        self.audit_repo.append_row(record)
        return audit_id

    def log(
        self,
        deal_id: str,
        object_type: str,
        object_id: str,
        action_type: str,
        before_value: str = "",
        after_value: str = "",
        acted_by_user_id: str = "",
        ip_address: str = "",
        note: str = "",
    ) -> str:
        dto = AuditLogCreateDTO(
            deal_id=deal_id,
            object_type=object_type,
            object_id=object_id,
            action_type=action_type,
            before_value=before_value,
            after_value=after_value,
            acted_by_user_id=acted_by_user_id,
            ip_address=ip_address,
            note=note,
        )

        return self.create_log(dto)