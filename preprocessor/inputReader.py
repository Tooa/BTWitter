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

import io
import json
import csv
import datetime
from os import path, listdir
import html.parser as HTMLParser
from timeHelper import convert_utc_to_local_time, convert_unix_time_to_local_time, date_regex


# Helper
def remove_newline(text):
    return text.replace('\n', '').replace('\r\r', '').replace('\r', '')


def unescape_html(text):
    text = text.replace("&amp;", "&")
    return HTMLParser.HTMLParser().unescape(text)


class InputJsonReader(object):
    def __init__(self, directory):
        self.directory = directory

    def stream_files_from_directory(self):
        list_of_files = [x for x in listdir(self.directory) if x.endswith('.json')]

        for f in list_of_files:
            print('Read current file:' + f)
            for tweet in self._stream_from_file(f):
                yield tweet

    def _stream_from_file(self, file):
        with io.open(path.join(self.directory, file), 'rU', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    yield json.loads(line)
                except ValueError:
                    print('The json object with line number %d could not be read' % i)


class TwitterReader(InputJsonReader):
    def stream(self, limit=None):
        for i, tweet in enumerate(self.stream_files_from_directory()):
            if limit and i >= limit: break

            created_at = tweet['created_at']
            # Check if it is tweet['created_at']['py/repr']
            if isinstance(created_at, dict):
                dt = datetime.datetime(
                    *map(lambda x: int(x) if x is not None else 0, date_regex.match(created_at['py/repr']).groups()))
            else:
                dt = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')

            local_time = convert_utc_to_local_time(dt)
            yield (local_time.date(), unescape_html(remove_newline(str(tweet['text']))))


class TopsyReader(InputJsonReader):
    def stream(self, limit=None):
        for i, tweet in enumerate(self.stream_files_from_directory()):
            if limit and i >= limit: break

            local_time = convert_unix_time_to_local_time(tweet['trackback_date']).date()

            yield (local_time, unescape_html(remove_newline(str(tweet['content']))))


class RawReader():
    def __init__(self, directory):
        self.directory = directory

    def stream(self, limit=None):
        list_of_files = filter(lambda x: x.endswith('.csv'), listdir(self.directory))
        for file in list_of_files:
            with io.open(path.join(self.directory, file), 'rU',) as csv_reader:
                reader = csv.reader(csv_reader, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break

                    dt = datetime.datetime.strptime(row[0], '%Y-%m-%d')
                    yield (dt.date(), unescape_html(row[1]))


