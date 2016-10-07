#!/usr/bin/env python

import re
import json
import argparse
import requests
import subprocess
import socket
import shlex
import time
import traceback

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VCAD agent')
    parser.add_argument('-url', '--url', type=str, required=True, help='Host to poll')
    parser.add_argument('-t', '--timeout', type=int, default=300, help='Polling timeout')
    parser.add_argument('-c', '--cmds', nargs='+', help='Allowed commands')
    args = parser.parse_args()
    allowed_cmds = [re.compile('^'+x+'$'.replace('^^','^').replace('$$', '$')) for x in args.cmds]
    hostname = socket.getfqdn()
    while True:
        try:
            result = requests.get('{}/subscribe/{}'.format(args.url, hostname), timeout=args.timeout)
            if result.ok and 'application/json' in result.headers.get('Content-Type', '').lower():
                result = result.json()
                for cmd in allowed_cmds:
                    if cmd.match(result['run']) is not None:
                        p = subprocess.Popen(shlex.split(result['run']), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        (stdout, stderr) = p.communicate()
                        data = {'action': 'notify', 'value': {'status': p.returncode, 'stdout': stdout, 'stderr': stderr}}
                        break
                else:
                    data = {'action': 'notify', 'value': {'status': 254, 'stdout': '', 'stderr': 'incorrect command'}}
        except Exception as e:
            print "Got error: {}, traceback: {}".format(e, traceback.format_exc())
            data = {'action': 'notify', 'value': {'status': 253, 'stdout': '', 'stderr': 'error executing command'}}
        finally:
            requests.post('{}/notify/{}'.format(args.url, hostname), json=data)

