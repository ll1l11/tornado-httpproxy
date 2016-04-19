# -*- coding:  utf-8 -*-
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

from tornado.options import define, options

logger = logging.getLogger('tornaod_httpproxy')
logger.setLevel(logging.DEBUG)

define('port', default=8888, help='run on the given port', type=int)


def fetch_request(url, callback, **kwargs):
    req = tornado.httpclient.HTTPRequest(url, **kwargs)
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch(req, callback, raise_error=False)


class MainHandler(tornado.web.RequestHandler):

    def handle_response(self, response):
        self._headers = tornado.httputil.HTTPHeaders()
        self.set_status(response.code, response.reason)
        for header, v in response.headers.get_all():
            if header in {'Content-Length'}:
                continue
            self.add_header(header, v)
        self.write(response.body)
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        logger.debug('Handle %s request to %s', self.request.method,
                     self.request.uri)
        body = self.request.body or None
        fetch_request(
            self.request.uri, self.handle_response,
            method=self.request.method, body=body,
            headers=self.request.headers, follow_redirects=False,
            allow_nonstandard_methods=True
        )

    @tornado.web.asynchronous
    def post(self):
        return self.get()


def main():
    tornado.options.parse_command_line()
    settings = dict(
        debug=True
    )
    application = tornado.web.Application([
        (r'.*', MainHandler),
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
