from apps.core.base.repository import BaseExcelRepository


class ExcelDocumentRepository(BaseExcelRepository):
    sheet_name = "documents"

    def get_last_document_id(self) -> str | None:
        rows = self.find_all()

        ids = [
            row.get("document_id")
            for row in rows
            if row.get("document_id")
        ]

        if not ids:
            return None

        return str(ids[-1])

    def find_by_deal(self, deal_id: str) -> list[dict]:
        return self.find_by("deal_id", deal_id)

    def find_one_by_document_id(self, document_id: str) -> dict | None:
        rows = self.find_all()

        for row in rows:
            if str(row.get("document_id") or "") == str(document_id):
                return row

        return None

    def filter_documents(self, filters: dict) -> list[dict]:
        rows = self.find_all()

        keyword = str(filters.get("keyword") or "").strip().lower()
        deal_id = str(filters.get("deal_id") or "").strip()
        phase_id = str(filters.get("phase_id") or "").strip()
        workstream_id = str(filters.get("workstream_id") or "").strip()
        document_type = str(filters.get("document_type") or "").strip()
        status = str(filters.get("status") or "").strip()
        access_level = str(filters.get("access_level") or "").strip()
        owner_user_id = str(filters.get("owner_user_id") or "").strip()

        template_only = bool(filters.get("template_only"))
        evidence_only = bool(filters.get("evidence_only"))
        report_only = bool(filters.get("report_only"))
        show_deleted = bool(filters.get("show_deleted"))

        results = []

        for row in rows:
            deleted_flag = str(row.get("deleted_flag") or "0")

            if not show_deleted and deleted_flag == "1":
                continue

            if deal_id and str(row.get("deal_id") or "") != deal_id:
                continue

            if phase_id and str(row.get("phase_id") or "") != phase_id:
                continue

            if workstream_id and str(row.get("workstream_id") or "") != workstream_id:
                continue

            if document_type and str(row.get("document_type") or "") != document_type:
                continue

            if status and str(row.get("status") or "") != status:
                continue

            if access_level and str(row.get("access_level") or "") != access_level:
                continue

            if owner_user_id and str(row.get("owner_user_id") or "") != owner_user_id:
                continue

            if template_only and str(row.get("is_template_flag") or "0") != "1":
                continue

            if evidence_only and str(row.get("is_evidence_flag") or "0") != "1":
                continue

            if report_only and str(row.get("is_report_flag") or "0") != "1":
                continue

            if keyword:
                document_title = str(row.get("document_title") or "").lower()
                file_name = str(row.get("file_name") or "").lower()
                tags = str(row.get("tags") or "").lower()
                document_purpose = str(row.get("document_purpose") or "").lower()
                category = str(row.get("category") or "").lower()
                subcategory = str(row.get("subcategory") or "").lower()

                if (
                    keyword not in document_title
                    and keyword not in file_name
                    and keyword not in tags
                    and keyword not in document_purpose
                    and keyword not in category
                    and keyword not in subcategory
                ):
                    continue

            results.append(row)

        return results