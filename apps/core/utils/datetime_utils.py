from django.utils import timezone
from apps.core.constants import DATETIME_FORMAT, DATE_FORMAT


def now_str() -> str:
    return timezone.localtime().strftime(DATETIME_FORMAT)


def today_str() -> str:
    return timezone.localtime().strftime(DATE_FORMAT)