from datetime import date, datetime

from apps.approvals.services import ApprovalService
from apps.audit.services import AuditLogService
from apps.deals.services import DealService
from apps.raid.services import RaidService
from apps.tasks.services import TaskService


class DashboardService:
    def __init__(
        self,
        deal_service: DealService | None = None,
        task_service: TaskService | None = None,
        raid_service: RaidService | None = None,
        approval_service: ApprovalService | None = None,
        audit_service: AuditLogService | None = None,
    ):
        self.deal_service = deal_service or DealService()
        self.task_service = task_service or TaskService()
        self.raid_service = raid_service or RaidService()
        self.approval_service = approval_service or ApprovalService()
        self.audit_service = audit_service or AuditLogService()

    def get_dashboard_context(self) -> dict:
        deals = self.deal_service.filter_deals({"show_archived": False})
        tasks = self.task_service.filter_tasks({"show_cancelled": False})
        raid_items = self.raid_service.filter_items({"show_closed": False})
        approvals = self.approval_service.filter_approvals({})
        audit_logs = self.audit_service.filter_logs({})

        active_deals = [
            deal for deal in deals
            if str(deal.get("deal_status") or "") not in ["COMPLETED", "CANCELLED", "ARCHIVED"]
            and str(deal.get("is_active") or "1") != "0"
        ]

        incomplete_tasks = [
            task for task in tasks
            if str(task.get("status") or "") not in ["DONE", "CANCELLED"]
        ]

        overdue_tasks = [
            task for task in incomplete_tasks
            if self._is_overdue(task.get("due_date"))
        ]

        unresolved_raid_items = [
            item for item in raid_items
            if str(item.get("status") or "") in ["OPEN", "IN_PROGRESS", "WATCH"]
        ]

        pending_approvals = [
            approval for approval in approvals
            if str(approval.get("approval_status") or "") == "REQUESTED"
        ]

        recent_logs = audit_logs[:10]
        upcoming_tasks = self._sort_tasks_by_due_date(incomplete_tasks)[:10]
        recent_deals = list(reversed(deals))[:5]

        return {
            "active_deal_count": len(active_deals),
            "incomplete_task_count": len(incomplete_tasks),
            "overdue_task_count": len(overdue_tasks),
            "unresolved_raid_count": len(unresolved_raid_items),
            "pending_approval_count": len(pending_approvals),
            "recent_logs": recent_logs,
            "upcoming_tasks": upcoming_tasks,
            "recent_deals": recent_deals,
        }

    def _is_overdue(self, due_date_value) -> bool:
        due_date = self._parse_date(due_date_value)

        if due_date is None:
            return False

        return due_date < date.today()

    def _sort_tasks_by_due_date(self, tasks: list[dict]) -> list[dict]:
        return sorted(
            tasks,
            key=lambda task: self._parse_date(task.get("due_date")) or date.max,
        )

    def _parse_date(self, value) -> date | None:
        if not value:
            return None

        text = str(value).strip()

        if not text:
            return None

        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue

        return None