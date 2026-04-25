def next_id(prefix: str, last_value: str | None, digits: int = 6) -> str:
    """
    例:
    last_value=None       -> DEAL-000001
    last_value=DEAL-000001 -> DEAL-000002
    """
    if not last_value:
        return f"{prefix}-{1:0{digits}d}"

    try:
        num = int(str(last_value).split("-")[-1])
    except (ValueError, IndexError):
        num = 0

    return f"{prefix}-{num + 1:0{digits}d}"