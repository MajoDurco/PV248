#!/usr/bin/env python3

import json
import sys

from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

NOT_FINISHED = 0
FINISHED = 1

class GameException(Exception):
  pass
class GameManagerException(Exception):
  pass

class Game():
  def __init__(self, game_id, name):
    self.id = game_id
    self.name = name
    self.board = [
      [ 0, 0, 0 ],
      [ 0, 0, 0 ],
      [ 0, 0, 0 ],
    ]
    self.player_turn = 1
    self.status = NOT_FINISHED
    self.winner = None
  
  def is_players_turn(self, player_id):
    return self.player_turn == player_id
  
  def are_coordinates_valid(self, x, y):
    return x >= 0 and x < 3 and y >= 0 and y < 3

  def is_place_empty(self, x , y):
    return self.board[y][x] == 0

  def get_next_turn_player(self):
    if self.player_turn == 1:
      return 2
    else:
      return 1
  
  def toggle_player(self):
    self.player_turn = self.get_next_turn_player()
  
  def check_full_board(self):
    for row in self.board:
      for column in row:
        if column == 0:
          return False
    return True

  def is_move_victory(self, x, y):
    if self.board[0][x] == self.board[1][x] == self.board[2][x]:
        return True
    if self.board[y][0] == self.board[y][1] == self.board[y][2]:
        return True
    if x == y and self.board[0][0] == self.board[1][1] == self.board[2][2]:
        return True
    if x + y == 2 and self.board[0][2] == self.board[1][1] == self.board[2][0]:
        return True
    return False
  
  def move(self, player_id, x, y):
    if self.status == FINISHED:
      raise GameException('Game is finished cannot move')
    if not self.is_players_turn(player_id):
      raise GameException('Not your turn')
    if not self.are_coordinates_valid(x, y):
      raise GameException('Wrong coordinates')
    if not self.is_place_empty(x, y):
      raise GameException('Place alredy taken')
    
    self.board[y][x] = self.player_turn
    if self.is_move_victory(x, y):
      self.winner = self.player_turn
      self.status = FINISHED
    elif self.check_full_board():
      self.winner = 0
      self.status = FINISHED
    else:
      self.toggle_player()

class GamesManager():
  def __init__(self):
    self.games = {}
    self.next_game_id = 0

  def create_game(self, name):
    game = Game(self.next_game_id, name)
    self.games[self.next_game_id] = game
    self.next_game_id += 1
    return game
  
  def get_game(self, game_id):
    if not game_id in self.games:
      raise GameManagerException('Game does not exist')
    return self.games[game_id]

  def get_game_status(self, game_id):
    game = self.get_game(game_id)
    if game.status == FINISHED:
      return {
        'winner': int(game.winner)
      }
    else:
      return {
        'board': game.board,
        'next': int(game.get_next_turn_player()),
      }

class Handler(BaseHTTPRequestHandler):
  def do_HEAD(self):
    self.send_error(405, 'HEAD not supported')
    
  def do_POST(self):
    self.send_error(405, 'GET not supported')

  def set_headers(self, content_len):
    for keyword, value in self.headers.items():
        self.send_header(keyword, value)
    self.send_header('Content-Length', content_len)
    self.end_headers()
  
  def handle_start(self):
    name = parse_qs(self.parsed.query).get('name')
    new_game = None
    if name is None:
      new_game = gameManager.create_game('')
    else:
      new_game = gameManager.create_game(name[0])
    self.send_result(200, {
      'id': int(new_game.id)
    })

  def handle_play(self):
    params = parse_qs(self.parsed.query)
    game = params.get('game')
    player = params.get('player')
    x = params.get('x')
    y = params.get('y')
    if game is None or player is None or x is None or y is None:
      self.send_result(400, {
        'status': 'bad',
        'message': 'Wrong query arguments for /play'
      })
    try:
      game = int(game[0])
      player = int(player[0])
      x = int(x[0])
      y = int(y[0])
    except ValueError:
      self.send_result(400, {
        'status': 'bad',
        'message': 'All query parameters should be integers'
      })
    try:
      game = gameManager.get_game(game)
      game.move(player, x, y)
      self.send_result(200, { 'status': 'ok' })
    except GameManagerException as gameMngErr:
      self.send_result(400, {
        'status': 'bad',
        'message': str(gameMngErr)
      })
    except GameException as gameErr:
      self.send_result(200, {
        'status': 'bad',
        'message': str(gameErr)
      })

  def handle_status(self):
    game = parse_qs(self.parsed.query).get('game')
    if game is None:
      self.send_result(400, {
        'status': 'bad',
        'message': 'Game id is missing'
      })
    try:
        game = int(game[0])
    except ValueError:
      self.send_result(400, {
        'status': 'bad',
        'message': 'All query parameters should be integers'
      })
    try:
      status = gameManager.get_game_status(game)
      self.send_result(200, status)
    except GameManagerException as gameMngErr:
      self.send_result(400, {
        'status': 'bad',
        'message': str(gameMngErr)
      })
    except GameException as gameErr:
      self.send_result(200, {
        'status': 'bad',
        'message': str(gameErr)
      })

  def do_GET(self):
    self.output = {}
    self.parsed = urlparse(self.path)
    path = self.parsed.path
    if path == '/start':
      self.handle_start()
    elif path == '/play':
      self.handle_play()
    elif path == '/status':
      self.handle_status()
    else:
      self.send_error(404, 'Path not found')
      return

  def send_result(self, status_code, data):
    data = json.dumps(data)
    self.send_response(status_code)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Content-Length', str(len(data)))
    self.end_headers()

    self.wfile.write(bytes(data, 'UTF-8'))

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
  gameManager = GamesManager()

  main()
