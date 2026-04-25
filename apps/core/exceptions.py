class RepositoryError(Exception):
    """Repository層で発生する共通エラー"""
    pass


class RecordNotFoundError(RepositoryError):
    """対象レコードが見つからない場合のエラー"""
    pass