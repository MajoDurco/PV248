#!/usr/bin/env python3

import json
import os
import sys
import urllib

from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

GAME_STATUS = {
  
}

class Game():
  def __init__(self, name):
    self.name = name
    self.board = [
      [ 0, 0, 0],
      [ 0, 0, 0],
      [ 0, 0, 0],
    ]
    self.player_turn = 1
    self.status = 

class Games():
  def __init__(self):
    self.games = {}
    self.next_id = 0

  def createGame(self, name):
    self.games[self.next_id] = Game(name)
    self.next_id += 1

class Handler(BaseHTTPRequestHandler):
    # def do_GET(self):
    #     print(self.path)
    #     parsed = urlparse.urlsplit(self.path)

    #     action = parsed.path[1:]
    #     params = urlparse.parse_qs(parsed.query)
    #     if action == 'start':
    #         name = params['name'][0] if 'name' in params else ''
    #         return self.start_game(name)
    #     elif action == 'status':
    #         if 'game' not in params:
    #             return self.invalid_request(
    #                 code=400,
    #                 status='bad',
    #                 message='Missing parameter: game')
    #         try:
    #             game_id = int(params['game'][0])
    #         except ValueError:
    #             return self.invalid_request(
    #                 code=400,
    #                 status='bad',
    #                 message='Wrong parameter (non-integer): game'
    #             )
    #         return self.state_of_game(game_id)
    #     elif action == 'play':
    #         if 'game' not in params or \
    #             'player' not in params or \
    #             'x' not in params or \
    #             'y' not in params:
    #             return self.invalid_request(
    #                 code=400,
    #                 status='bad',
    #                 message='Missing parameter'
    #             )
    #         try:
    #             game_id = int(params['game'][0])
    #             player_id = int(params['player'][0])
    #             x = int(params['x'][0])
    #             y = int(params['y'][0])
    #         except ValueError:
    #             return self.invalid_request(
    #                 code=400,
    #                 status='bad',
    #                 message='Wrong parameter (non-integer)'
    #             )
    #         return self.play_turn(game_id, player_id, x, y)
    #     else:
    #         return self.invalid_request(
    #             code=400,
    #             status='bad',
    #             message='Invalid action requested (start|status|play)'
    #         )

class ThreadingServer(ThreadingMixIn, HTTPServer):
  pass

def main():
  with ThreadingServer(('', int(port)), Handler) as httpd:
    httpd.serve_forever()

if __name__ == '__main__':
  number_of_arguments = 2;

  if len(sys.argv) != number_of_arguments:
    sys.exit('Wrong number of arguments')

  _, port = sys.argv
  main()