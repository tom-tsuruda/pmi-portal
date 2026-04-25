from dataclasses import dataclass


@dataclass
class DocumentUploadDTO:
    deal_id: str
    phase_id: str
    workstream_id: str
    document_title: str
    document_type: str
    category: str = ""
    subcategory: str = ""
    owner_user_id: str = ""
    access_level: str = "INTERNAL"
    linked_task_id: str = ""
    linked_raid_id: str = ""
    tags: str = ""
    document_purpose: str = ""
    is_template_flag: int = 0
    is_evidence_flag: int = 0
    is_report_flag: int = 0