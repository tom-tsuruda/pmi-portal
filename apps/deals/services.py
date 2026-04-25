from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.deals.dtos import DealCreateDTO
from apps.deals.repositories import ExcelDealRepository


class DealService:
    def __init__(self, deal_repo: ExcelDealRepository | None = None):
        self.deal_repo = deal_repo or ExcelDealRepository()

    def list_deals(self) -> list[dict]:
        return self.deal_repo.filter_deals({"show_archived": False})

    def filter_deals(self, filters: dict) -> list[dict]:
        return self.deal_repo.filter_deals(filters)

    def get_deal(self, deal_id: str) -> dict:
        return self.deal_repo.find_one("deal_id", deal_id)

    def create_deal(self, dto: DealCreateDTO) -> str:
        last_id = self.deal_repo.get_last_deal_id()
        deal_id = next_id("DEAL", last_id)

        current_time = now_str()

        record = {
            "deal_id": deal_id,
            "deal_code": deal_id,
            "deal_name": dto.deal_name,
            "target_company_name": dto.target_company_name,
            "deal_type": dto.deal_type,

            "integration_model": "",
            "region_main": dto.region_main,
            "country_scope": "",
            "industry": "",

            "regulated_industry_flag": 0,
            "personal_data_flag": 0,
            "special_category_data_flag": 0,

            "tsa_flag": 0,
            "tsa_period_months": "",
            "brand_policy": "",

            "close_planned_date": "",
            "day1_date": "",
            "day100_date": "",

            "deal_status": "DRAFT",
            "display_level": "STANDARD",
            "mandatory_task_threshold": "HIGH",
            "template_control_mode": "AUTO",

            "owner_user_id": dto.owner_user_id,
            "imo_lead_user_id": "",
            "sponsor_user_id": "",

            "description": dto.description,
            "beginner_guidance": "この案件はPMI管理の基本単位です。まずはDay1、Day100、主要タスク、リスクを順番に整理してください。",

            "created_at": current_time,
            "updated_at": current_time,
            "is_active": 1,
        }

        self.deal_repo.append_row(record)
        return deal_id

    def update_status(self, deal_id: str, deal_status: str) -> None:
        updates = {
            "deal_status": deal_status,
            "updated_at": now_str(),
        }

        # ARCHIVED は通常一覧から非表示にする
        if deal_status == "ARCHIVED":
            updates["is_active"] = 0
        else:
            updates["is_active"] = 1

        self.deal_repo.update_row("deal_id", deal_id, updates)

    def archive_deal(self, deal_id: str) -> None:
        self.update_status(deal_id, "ARCHIVED")

    def reactivate_deal(self, deal_id: str) -> None:
        self.deal_repo.update_row(
            "deal_id",
            deal_id,
            {
                "deal_status": "ACTIVE",
                "is_active": 1,
                "updated_at": now_str(),
            },
        )