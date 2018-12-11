#!/usr/bin/env python3

import json
import os
import sys
import urllib

from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

NOT_FINISHED = 0
FINISHED = 1

class WrongPlayerTurn(Exception):
  pass
class WrongCoordinates(Exception):
  pass
class BoardPlaceNotEmpty(Exception):
  pass
class GameIsFinishedCannotMove(Exception):
  pass

class Game():
  def __init__(self, name):
    self.name = name
    self.board = [
      [ 0, 0, 0],
      [ 0, 0, 0],
      [ 0, 0, 0],
    ]
    self.player_turn = 1
    self.status = NOT_FINISHED
    self.winner = None
  
  def is_players_turn(self, player_id):
    return self.player_turn == player_id
  
  def are_coordinates_valid(self, x, y):
    return x >= 0 and x < 3 and y >= 0 and y < 3

  def is_place_empty(self, x , y):
    return self.board[x][y] == 0

  def get_next_turn_player(self):
    if self.player_turn == 1:
      return 2
    else:
      return 1
  
  def toggle_player(self):
    self.player_turn = self.get_next_turn_player()
  
  def check_full_board(self):
    is_full = True
    for row in self.board:
      for column in row:
        if column != 0:
          is_full = False
          break
    return is_full

  def is_move_victory(self, x, y):
    if self.board[0][y] == self.board[1][y] == self.board[2][y]:
        return True
    if self.board[x][0] == self.board[x][1] == self.board[x][2]:
        return True
    if x == y and self.board[0][0] == self.board[1][1] == self.board[2][2]:
        return True
    if x + y == 2 and self.board[0][2] == self.board[1][1] == self.board[2][0]:
        return True
    return False
  
  def move(self, player_id, x, y):
    if self.status == FINISHED:
      raise GameIsFinishedCannotMove('Game is finished cannot move')
    if not self.is_players_turn(player_id):
      raise WrongPlayerTurn('Not your turn')
    if not self.are_coordinates_valid(x, y):
      raise WrongCoordinates('Wrong coordinates')
    if not self.is_place_empty(x, y):
      raise BoardPlaceNotEmpty('Place alredy taken')
    
    self.board[x][y] = self.player_turn
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
    self.next_id = 0

  def createGame(self, name):
    game = Game(name)
    self.games[self.next_id] = game
    self.next_id += 1
    return game

class Handler(BaseHTTPRequestHandler):
    pass
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

# class ThreadingServer(ThreadingMixIn, HTTPServer):
#   pass

# def main():
#   with ThreadingServer(('', int(port)), Handler) as httpd:
#     httpd.serve_forever()

# if __name__ == '__main__':
#   number_of_arguments = 2;

#   if len(sys.argv) != number_of_arguments:
#     sys.exit('Wrong number of arguments')

#   _, port = sys.argv
#   main()

games = GamesManager()