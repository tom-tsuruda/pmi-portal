from dataclasses import dataclass


@dataclass
class DealCreateDTO:
    deal_name: str
    target_company_name: str
    deal_type: str
    region_main: str = ""
    owner_user_id: str = ""
    description: str = ""