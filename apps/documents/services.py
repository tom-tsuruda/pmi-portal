from pathlib import Path

from django.conf import settings

from apps.core.exceptions import RecordNotFoundError, RepositoryError
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

    def list_templates(self) -> list[dict]:
        """
        テンプレートライブラリに登録されたテンプレートだけを取得する。
        """
        filters = {
            "template_only": True,
            "show_deleted": False,
        }
        return self.document_repo.filter_documents(filters)

    def find_related_templates_for_task(
        self,
        task: dict,
        templates: list[dict] | None = None,
        limit: int = 3,
    ) -> list[dict]:
        """
        タスクの phase_id / workstream_id / title / description をもとに、
        関連しそうなテンプレートを返す。

        優先順位:
        1. Phase と Workstream が両方一致
        2. Workstream が一致
        3. Phase が一致
        4. タイトル・説明・タグのキーワードが一致
        """
        if templates is None:
            templates = self.list_templates()

        task_phase = str(task.get("phase_id") or "").strip()
        task_workstream = str(task.get("workstream_id") or "").strip()
        task_title = str(task.get("title") or "").strip().lower()
        task_description = str(task.get("description") or "").strip().lower()
        task_text = f"{task_title} {task_description}"

        scored_templates = []

        for template in templates:
            template_phase = str(template.get("phase_id") or "").strip()
            template_workstream = str(template.get("workstream_id") or "").strip()
            template_title = str(template.get("document_title") or "").strip().lower()
            template_category = str(template.get("category") or "").strip().lower()
            template_subcategory = str(template.get("subcategory") or "").strip().lower()
            template_tags = str(template.get("tags") or "").strip().lower()
            template_purpose = str(template.get("document_purpose") or "").strip().lower()

            score = 0

            if task_phase and template_phase == task_phase:
                score += 30

            if task_workstream and template_workstream == task_workstream:
                score += 40

            if task_phase and template_phase == task_phase and task_workstream and template_workstream == task_workstream:
                score += 40

            keyword_source = " ".join(
                [
                    template_title,
                    template_category,
                    template_subcategory,
                    template_tags,
                    template_purpose,
                ]
            )

            if task_title and self._has_keyword_overlap(task_text, keyword_source):
                score += 15

            if score <= 0:
                continue

            item = template.copy()
            item["_match_score"] = score
            scored_templates.append(item)

        scored_templates.sort(
            key=lambda item: (
                -int(item.get("_match_score") or 0),
                str(item.get("document_title") or ""),
            )
        )

        return scored_templates[:limit]

    def build_task_template_map(self, tasks: list[dict], limit: int = 3) -> dict[str, list[dict]]:
        """
        タスク一覧画面用。
        task_id -> 関連テンプレート一覧 の辞書を作る。
        """
        templates = self.list_templates()
        result = {}

        for task in tasks:
            task_id = str(task.get("task_id") or "").strip()

            if not task_id:
                continue

            result[task_id] = self.find_related_templates_for_task(
                task=task,
                templates=templates,
                limit=limit,
            )

        return result

    def _has_keyword_overlap(self, task_text: str, keyword_source: str) -> bool:
        """
        簡易キーワード一致。
        日本語でも英語でも、含まれていれば関連ありとする。
        """
        if not task_text or not keyword_source:
            return False

        keywords = [
            "day1",
            "day100",
            "faq",
            "通知",
            "顧客",
            "サプライヤ",
            "従業員",
            "給与",
            "支払",
            "請求",
            "権限",
            "アクセス",
            "it",
            "契約",
            "coc",
            "支配権",
            "raci",
            "責任分担",
            "steerco",
            "報告",
            "議事録",
            "個人情報",
            "dpiA".lower(),
            "privacy",
            "法務",
            "finance",
            "hr",
            "comms",
            "pmo",
        ]

        combined = f"{task_text} {keyword_source}".lower()

        for keyword in keywords:
            normalized_keyword = keyword.lower()
            if normalized_keyword in task_text and normalized_keyword in keyword_source:
                return True

            if normalized_keyword in combined and normalized_keyword in keyword_source:
                return True

        return False

    def get_document(self, document_id: str) -> dict:
        document = self.document_repo.find_one_by_document_id(document_id)

        if not document:
            raise RecordNotFoundError(f"documents: document_id={document_id} not found")

        return document

    def get_absolute_file_path(self, document_id: str) -> Path:
        document = self.get_document(document_id)
        storage_path = str(document.get("storage_path") or "").strip()

        if not storage_path:
            raise RepositoryError("この資料には保存先ファイルが登録されていません。")

        root = Path(settings.PMI_STORAGE_ROOT).resolve()
        absolute_path = (root / storage_path).resolve()

        if root not in absolute_path.parents and absolute_path != root:
            raise RepositoryError("不正なファイルパスです。")

        if not absolute_path.exists() or not absolute_path.is_file():
            raise RepositoryError(f"ファイルが見つかりません: {storage_path}")

        return absolute_path

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