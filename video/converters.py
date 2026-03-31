from datetime import date, datetime

from django.utils import timezone
from django.utils.dateparse import parse_date

timezone = timezone.get_default_timezone()

class DateConverter:
    regex = "[0-9]{4}-[0-9]{2}-[0-9]{2}"
    format = "%Y-%m-%d"

    def to_python(self, value):
        parsed = parse_date(value)
        if parsed is not None:
            return parsed

        # Fallback for unexpected inputs; keeps the converter resilient.
        return value

    def to_url(self, value):
        if isinstance(value, str):
            return value

        if isinstance(value, datetime):
            value = value.date()

        if isinstance(value, date):
            return value.strftime(self.format)

        return str(value)
