from typing import Any

from apps.core.exceptions import RecordNotFoundError, RepositoryError
from apps.core.utils.excel_helpers import ExcelWorkbookManager


class BaseExcelRepository:
    """
    Excelを簡易DBとして扱うための基底Repository。
    1行目をヘッダー行として扱う。
    """

    sheet_name: str = ""

    def __init__(self, workbook_manager: ExcelWorkbookManager | None = None):
        self.workbook_manager = workbook_manager or ExcelWorkbookManager()

    def _load_sheet(self):
        if not self.sheet_name:
            raise RepositoryError("sheet_name is not defined.")

        wb = self.workbook_manager.load()
        ws = self.workbook_manager.get_sheet(wb, self.sheet_name)
        return wb, ws

    def _headers(self, ws) -> list[str]:
        headers = [cell.value for cell in ws[1]]

        if not headers or all(h is None for h in headers):
            raise RepositoryError(
                f"Sheet '{self.sheet_name}' has no header row."
            )

        return [str(h).strip() if h is not None else "" for h in headers]

    def _row_to_dict(self, headers: list[str], row) -> dict[str, Any]:
        values = [cell.value for cell in row]
        return dict(zip(headers, values))

    def find_all(self) -> list[dict[str, Any]]:
        wb, ws = self._load_sheet()
        headers = self._headers(ws)

        results = []
        for row in ws.iter_rows(min_row=2):
            if all(cell.value is None for cell in row):
                continue

            results.append(self._row_to_dict(headers, row))

        return results

    def find_by(self, key: str, value: Any) -> list[dict[str, Any]]:
        return [
            row
            for row in self.find_all()
            if str(row.get(key, "")) == str(value)
        ]

    def find_one(self, key: str, value: Any) -> dict[str, Any]:
        for row in self.find_all():
            if str(row.get(key, "")) == str(value):
                return row

        raise RecordNotFoundError(
            f"{self.sheet_name}: {key}={value} not found"
        )

    def append_row(self, data: dict[str, Any]) -> None:
        wb, ws = self._load_sheet()
        headers = self._headers(ws)

        row = [data.get(header, "") for header in headers]
        ws.append(row)

        self.workbook_manager.save(wb)

    def update_row(self, key: str, value: Any, updates: dict[str, Any]) -> None:
        wb, ws = self._load_sheet()
        headers = self._headers(ws)

        if key not in headers:
            raise RepositoryError(
                f"Key column '{key}' not found in sheet '{self.sheet_name}'."
            )

        key_idx = headers.index(key) + 1

        for row_idx in range(2, ws.max_row + 1):
            current_value = ws.cell(row=row_idx, column=key_idx).value

            if str(current_value) == str(value):
                for col_idx, header in enumerate(headers, start=1):
                    if header in updates:
                        ws.cell(row=row_idx, column=col_idx).value = updates[header]

                self.workbook_manager.save(wb)
                return

        raise RecordNotFoundError(
            f"{self.sheet_name}: {key}={value} not found"
        )