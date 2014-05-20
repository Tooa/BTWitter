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

#!/usr/bin/env python3
from btwitter import app


class WebFactionMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = '/BTWitter'
        return self.app(environ, start_response)


if __name__ == '__main__':
    #Use this if your app isn't located at /
    #app.wsgi_app = WebFactionMiddleware(app.wsgi_app)
    app.run(host='0.0.0.0', port=3031)
