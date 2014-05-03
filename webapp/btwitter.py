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

from btwitter import create_app
import logging
app = create_app()

try:
    from log_colorizer import make_colored_stream_handler
    handler = make_colored_stream_handler()
    app.logger.handlers = []
    app.logger.addHandler(handler)
    import werkzeug
    werkzeug._internal._log('debug', '<-- I am with stupid')
    logging.getLogger('werkzeug').handlers = []
    logging.getLogger('werkzeug').addHandler(handler)

    handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
except:
    pass


try:
    import wsreload
except ImportError:
    app.logger.debug('wsreload not found')
else:
    url = "http://btwitter.l:12221/*"

    def log(httpserver):
        app.logger.debug('WSReloaded after server restart')
    wsreload.monkey_patch_http_server({'url': url}, callback=log)
    app.logger.debug('HTTPServer monkey patched for url %s' % url)

try:
    from wdb.ext import WdbMiddleware, add_w_builtin
except ImportError:
    pass
else:
    add_w_builtin()
    app.wsgi_app = WdbMiddleware(app.wsgi_app, start_disabled=True)

app.run(debug=True, threaded=True, host='localhost', port=12221)
