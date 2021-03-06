"""Copyright 2014 Uli Fahrer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import re
from datetime import timezone, datetime

date_regex = re.compile(r'datetime\/datetime\.datetime\((\d{4}), (\d{1,2}), (\d{1,2}),? ?(\d{1,2})?,? ?(\d{1,2})?,? ?(\d{1,2})?\)')


def convert_utc_to_local_time(date):
    return date.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convert_unix_time_to_local_time(unix_time):
    return datetime.fromtimestamp(unix_time)
