#!/usr/bin/env python3

import re
import sys
import http.client
import json

from http.server import HTTPServer, SimpleHTTPRequestHandler

def to_json(data):
    try:
      return json.loads(data)
    except ValueError:
      return False

def parseUrl(url):
  without_http = re.sub(r'^http[s]://','', url)
  split = without_http.split('/', 1)
  base = split[0]
  if len(split) == 2:
    rest = '/' + split[1]
  else:
    rest = '/'
  return (base, rest)

class ServerHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    url_base, url_rest = parseUrl(url)
    response = {}
    try:
      connection = http.client.HTTPSConnection(url_base, timeout=1)

      req_headers = dict(self.headers)
      if 'Host' in req_headers:
          del req_headers['Host']

      connection.request('GET', url_rest, headers=req_headers)
      response = connection.getresponse()
      headers = dict(response.getheaders())
      data = response.read().decode('utf-8', 'ignore')
      response = {
        'code': response.status,
        'headers': headers,
      }
      json_data = to_json(data)
      if json_data is not False:
        response['json'] = json_data
      else:
        response['content'] = data
    except :
      response = { 'code': 'timeout' }
    finally:
      self.send_json(response)
      connection.close()

  def do_POST(self):
    data_string = self.rfile.read(int(self.headers['Content-Length']))
    response = {}
    json_data = to_json(data_string)
    if not json_data:
      response['code'] = 'invalid json'
      return self.send_json(response)

    http_type = json_data.get('type', 'GET')
    request_url = json_data.get('url', None)
    content = json_data.get('content', None)
    headers = json_data.get('headers', {})
    timeout = json_data.get('timeout', 1)

    if not url or (http_type == 'POST' and content == None):
      response['code'] = 'invalid json'
      return self.send_json(response)

    url_base, url_rest = parseUrl(request_url)
    response = {}
    try:
      connection = http.client.HTTPSConnection(url_base, timeout=timeout)
      connection.request(http_type, url_rest, body=bytes(json.dumps(content), 'utf-8'), headers=headers)
      response = connection.getresponse()
      headers = dict(response.getheaders())
      data = response.read().decode('utf-8', 'ignore')
      response = {
        'code': response.status,
        'headers': headers,
      }
      json_data = to_json(data)
      if json_data is not False:
        response['json'] = json_data
      else:
        response['content'] = data
    except :
      response = { 'code': 'timeout' }
    finally:
      self.send_json(response)
      connection.close()


  def send_json(self, data):
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(bytes(json.dumps(data), 'utf-8'))

def main():
  with HTTPServer(('localhost', int(port)), ServerHandler) as httpd:
    httpd.serve_forever()
  
if __name__ == '__main__':
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, port, url = sys.argv
  main()
