from pathlib import Path

from django.conf import settings

from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.documents.dtos import DocumentUploadDTO
from apps.documents.repositories import ExcelDocumentRepository


class DocumentService:
    def __init__(self, document_repo: ExcelDocumentRepository | None = None):
        self.document_repo = document_repo or ExcelDocumentRepository()

    def list_documents(self, deal_id: str | None = None) -> list[dict]:
        filters = {
            "deal_id": deal_id or "",
            "show_deleted": False,
        }
        return self.document_repo.filter_documents(filters)

    def filter_documents(self, filters: dict) -> list[dict]:
        return self.document_repo.filter_documents(filters)

    def upload_document(self, dto: DocumentUploadDTO, uploaded_file) -> str:
        last_id = self.document_repo.get_last_document_id()
        document_id = next_id("DOC", last_id)

        original_name = uploaded_file.name
        file_path = Path(original_name)

        file_name = file_path.name
        file_ext = file_path.suffix.replace(".", "").lower()

        relative_folder = Path("deals") / dto.deal_id / dto.phase_id
        absolute_folder = Path(settings.PMI_STORAGE_ROOT) / relative_folder
        absolute_folder.mkdir(parents=True, exist_ok=True)

        safe_file_name = f"{document_id}_{file_name}"
        absolute_path = absolute_folder / safe_file_name
        relative_path = relative_folder / safe_file_name

        with open(absolute_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        current_time = now_str()

        record = {
            "document_id": document_id,
            "deal_id": dto.deal_id,
            "phase_id": dto.phase_id,
            "workstream_id": dto.workstream_id,

            "document_code": document_id,
            "document_title": dto.document_title,
            "document_type": dto.document_type,
            "category": dto.category,
            "subcategory": dto.subcategory,

            "file_name": file_name,
            "file_ext": file_ext,
            "storage_path": str(relative_path).replace("\\", "/"),
            "folder_path": str(relative_folder).replace("\\", "/"),

            "version_current": "1.0",
            "status": "DRAFT",

            "owner_user_id": dto.owner_user_id,
            "approver_user_id": "",
            "access_level": dto.access_level,

            "linked_task_id": dto.linked_task_id,
            "linked_raid_id": dto.linked_raid_id,
            "linked_decision_id": "",

            "is_template_flag": dto.is_template_flag,
            "is_evidence_flag": dto.is_evidence_flag,
            "is_report_flag": dto.is_report_flag,

            "tags": dto.tags,
            "document_purpose": dto.document_purpose,
            "beginner_guidance": "この資料は、PMI作業の証跡・参考資料・テンプレートとして管理されます。案件、フェーズ、ワークストリームとの紐づきを確認してください。",

            "created_at": current_time,
            "updated_at": current_time,
            "deleted_flag": 0,
        }

        self.document_repo.append_row(record)
        return document_id

    def soft_delete_document(self, document_id: str) -> None:
        self.document_repo.update_row(
            "document_id",
            document_id,
            {
                "status": "DELETED",
                "deleted_flag": 1,
                "updated_at": now_str(),
            },
        )