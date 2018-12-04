#!/usr/bin/env python3

import json
import logging
import os
import socketserver
import sys
import urllib

from http.server import HTTPServer, CGIHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

class ThreadingServer(ThreadingMixIn, HTTPServer):
  pass

def file_by_chunks(file, chunk_size=1024):
  while True:
    data = file.read(chunk_size)
    if data:
      yield data
    else:
      break

class CGIHandler(CGIHTTPRequestHandler):

  def do_GET(self):
    self.handle_request()

  def do_POST(self):
    self.handle_request()

  def do_HEAD(self):
    self.handle_request()

  def handle_static_content(self, file_path):
    file_size = os.path.getsize(file_path)
    self.send_response(200)
    self.send_header('Content-Length', str(file_size))
    self.end_headers()

    file = open(file_path, 'rb')
    for chunk in file_by_chunks(file):
      self.wfile.write(chunk)

  def handle_cgi(self, req_path, query):
    rest_path_with_query = '{}?{}'.format(req_path, query) if query else req_path
    self.cgi_info = argument_dir.rstrip('/'), rest_path_with_query
    self.run_cgi()

  def handle_request(self):
    parsed_req_path = urlparse(self.path)
    req_path = parsed_req_path.path[1:]
    query = parsed_req_path.query
    file_path = os.path.join(argument_dir, req_path)
    if os.path.isfile(file_path):
      if file_path.endswith('.cgi'):
        self.handle_cgi(req_path, query)
      else:
        self.handle_static_content(file_path)
    else:
      self.send_error(404, explain='File was not found!')

def main():
  with ThreadingServer(('localhost', int(port)), CGIHandler) as httpd:
    httpd.serve_forever()

if __name__ == '__main__':
  number_of_arguments = 3;

  if len(sys.argv) != number_of_arguments:
    sys.exit('Wrong number of arguments')

  _, port, argument_dir = sys.argv
  main()