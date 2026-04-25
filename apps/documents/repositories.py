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