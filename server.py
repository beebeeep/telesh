#!/usr/bin/env python3


import json
import logging
import argparse
import traceback
from tornado import gen, httpserver, web, ioloop, concurrent, escape

logging.basicConfig(level=logging.DEBUG)

class NotifyHandler(web.RequestHandler):
    def initialize(self, subs):
        self._subs = subs

    @gen.coroutine
    def post(self, host=None):
        if host not in self._subs:
            logging.error("Notify for unknown host %s, subscriptions are %s", host, self._subs.keys())
            self.set_status(404)
            return

        run = self.get_argument('run', None)
        try:
            print(self.request.body)
            req = json.loads(escape.to_unicode(self.request.body))
            if 'value' not in req or req['action'] not in ['run', 'notify']:
                raise ValueError
        except (ValueError, KeyError) as e:
            print("Traceback: %s", traceback.format_exc())
            self.set_status(400)
            self.write({'result': 'ERROR', 'reason': 'cannot parse request'})
            return

        response = None

        if req['action'] == 'run':
            self._subs[host]['run'].set_result({'run': req['value']})
            response = yield self._subs[host]['result']
            logging.debug("Removing subscription for %s", host)
            logging.debug("Subscriptions now are %s", self._subs.keys())
            del self._subs[host]
        elif req['action'] == 'notify':
            self._subs[host]['result'].set_result({'result': req['value']})
            response = {'result': 'OK'}
        else:
            self.set_status(400)

        self.write(response)


class SubscriptionHandler(web.RequestHandler):
    def initialize(self, subs):
        self._subs = subs

    @gen.coroutine
    def get(self, host=None):
        if host not in self._subs:
            logging.debug("New subscription for {}".format(host))
            self._subs[host] = {'run': concurrent.Future(), 'result': concurrent.Future()}
        what = yield self._subs[host]['run']
        self.write(what)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VCAD agent server')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to listen')
    args = parser.parse_args()

    subscriptions = {}
    app = web.Application([
        (r"/subscribe/(?P<host>[-.A-z0-9]+)", SubscriptionHandler, {'subs': subscriptions}),
        (r"/notify/(?P<host>[-.A-z0-9]+)", NotifyHandler, {'subs': subscriptions})
    ])
    app.listen(args.port)
    ioloop.IOLoop.current().start()



