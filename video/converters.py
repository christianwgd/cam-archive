from django.utils import timezone
from django.utils.dateparse import parse_datetime

timezone = timezone.get_default_timezone()

class DateConverter:
    regex = "[0-9]{4}-[0-9]{2}-[0-9]{2}"
    format = "%Y-%m-%d"

    def to_python(self, value):
        naive = parse_datetime(value)
        return naive.replace(tzinfo=timezone).date()

    def to_url(self, value):
        return value.strftime(self.format)
