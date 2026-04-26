import shutil
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from apps.core.exceptions import RepositoryError


class BackupService:
    """
    PMI Excel台帳を1ファイルだけバックアップするサービス。
    毎回 storage/backups/master_data_backup.xlsx に上書きする。
    """

    backup_file_name = "master_data_backup.xlsx"

    def get_source_excel_path(self) -> Path:
        source_path = Path(settings.PMI_EXCEL_PATH).resolve()

        if not source_path.exists():
            raise RepositoryError(f"Excel台帳が見つかりません: {source_path}")

        if not source_path.is_file():
            raise RepositoryError(f"Excel台帳のパスがファイルではありません: {source_path}")

        return source_path

    def get_backup_dir(self) -> Path:
        storage_root = Path(settings.PMI_STORAGE_ROOT).resolve()
        backup_dir = storage_root / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def get_backup_path(self) -> Path:
        return self.get_backup_dir() / self.backup_file_name

    def create_backup(self) -> dict:
        source_path = self.get_source_excel_path()
        backup_path = self.get_backup_path()

        try:
            shutil.copy2(source_path, backup_path)
        except OSError as e:
            raise RepositoryError(f"バックアップ作成に失敗しました: {e}") from e

        return self.get_backup_info()

    def get_backup_info(self) -> dict:
        source_path = self.get_source_excel_path()
        backup_path = self.get_backup_path()

        exists = backup_path.exists() and backup_path.is_file()

        if exists:
            modified_at = timezone.datetime.fromtimestamp(
                backup_path.stat().st_mtime,
                tz=timezone.get_current_timezone(),
            )
            size_bytes = backup_path.stat().st_size
        else:
            modified_at = None
            size_bytes = 0

        return {
            "source_path": str(source_path),
            "backup_path": str(backup_path),
            "backup_file_name": self.backup_file_name,
            "exists": exists,
            "modified_at": modified_at,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 1) if size_bytes else 0,
        }

    def get_download_path(self) -> Path:
        backup_path = self.get_backup_path().resolve()
        backup_dir = self.get_backup_dir().resolve()

        if not backup_path.exists() or not backup_path.is_file():
            raise RepositoryError("バックアップファイルはまだ作成されていません。")

        if backup_dir not in backup_path.parents and backup_path != backup_dir:
            raise RepositoryError("不正なバックアップファイルパスです。")

        return backup_path