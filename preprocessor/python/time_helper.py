import re

from datetime import timezone, datetime

date_regex = re.compile(r'datetime\/datetime\.datetime\((\d{4}), (\d{1,2}), (\d{1,2}),? ?(\d{1,2})?,? ?(\d{1,2})?,? ?(\d{1,2})?\)')


def convert_utc_to_local_time(date):
    return date.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convert_unix_time_to_local_time(unix_time):
    return datetime.fromtimestamp(unix_time)
