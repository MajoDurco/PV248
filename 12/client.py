#!/usr/bin/env python3

import sys
import json
import urllib.request

def parse_json_response(response):
  try:
    str_response = response.read().decode('utf-8')
    return json.loads(str_response)
  except Exception as e: # TODO make specific
    print(e)
    return None

def call_server(path):
  return parse_json_response(urllib.request.urlopen(url+path))

def print_game_list():
  game_list = call_server('/list')
  for game in game_list:
    print('{} {}'.format(game['id'], game['name']))

def main():
  print_game_list()

if __name__ == '__main__':
  number_of_arguments = 3;

  if len(sys.argv) != number_of_arguments:
    sys.exit('Wrong number of arguments')

  _, host, port = sys.argv
  url = 'http://{}:{}'.format(host, str(port))
  main()
