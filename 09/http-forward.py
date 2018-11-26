#!/usr/bin/env python3

import re
import ssl
import sys
import http.client
import json
import socket

from http.server import HTTPServer, SimpleHTTPRequestHandler
from OpenSSL.SSL import TLSv1_2_METHOD, Context, Connection

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
  is_ssl = True if url.startswith('https://') else False
  return (base, rest, is_ssl)

def get_certificate_hosts(certificate):
  hosts = ''
  for extension_index in range(certificate.get_extension_count()):
    extension = certificate.get_extension(extension_index)
    if 'subjectAltName' in str(extension.get_short_name()):
      hosts = str(extension)
  hosts = hosts.split(', ')
  return [host[4:] if host.startswith('DNS:') else host for host in hosts]

def checkCertificate(url_base, url_rest, req_headers={}, request_type='GET'):
  connection = http.client.HTTPSConnection(url_base, timeout=1)
  certificate_is_valid = None
  certificate_host_names = None
  try:
    client = socket.socket()
    client.connect((url_base, 443))
    client_ssl = Connection(Context(TLSv1_2_METHOD), client)
    client_ssl.set_connect_state()
    client_ssl.set_tlsext_host_name(url_base.encode('UTF-8'))
    client_ssl.do_handshake()
    certificate_host_names = get_certificate_hosts(client_ssl.get_peer_certificate())
  except:
    pass
  finally:
    if client:
      client.close()
  try:
    connection.request(request_type, url_rest, headers=req_headers)
    certificate_is_valid = True
  except:
    certificate_is_valid = False
  return (certificate_is_valid, certificate_host_names)


class ServerHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    url_base, url_rest, is_ssl = parseUrl(url)
    response = {}
    try:
      req_headers = dict(self.headers)
      if 'Host' in req_headers:
          del req_headers['Host']
      cert_valid = None
      cert_host_names = None
      if is_ssl:
        cert_valid, cert_host_names = checkCertificate(url_base, url_rest, req_headers)

      context = ssl.create_default_context()
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE
      connection = http.client.HTTPSConnection(url_base, timeout=1, context=context)
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
      if cert_valid is not None:
        response['certificate valid'] = cert_valid
      if cert_host_names is not None:
        response['certificate for'] = cert_host_names
    except:
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

    url_base, url_rest, is_ssl = parseUrl(request_url)
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
