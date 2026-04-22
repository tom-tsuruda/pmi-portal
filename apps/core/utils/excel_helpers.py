from pathlib import Path
from openpyxl import load_workbook
from django.conf import settings
from apps.core.exceptions import RepositoryError


class ExcelWorkbookManager:
    def __init__(self, filepath: str | None = None):
        self.filepath = filepath or settings.PMI_EXCEL_PATH

    def load(self):
        path = Path(self.filepath)
        if not path.exists():
            raise RepositoryError(f"Excel file not found: {path}")
        return load_workbook(path)

    def save(self, workbook):
        workbook.save(self.filepath)

    def get_sheet(self, workbook, sheet_name: str):
        if sheet_name not in workbook.sheetnames:
            raise RepositoryError(f"Sheet not found: {sheet_name}")
        return workbook[sheet_name]