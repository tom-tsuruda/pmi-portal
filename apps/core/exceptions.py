class RepositoryError(Exception):
    pass


class RecordNotFoundError(RepositoryError):
    pass


class ValidationError(Exception):
    pass