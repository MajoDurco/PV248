#!/usr/bin/env python3

import sys
import json
import urllib.request

from time import sleep

class ConnectException(Exception):
  pass
class PlayException(Exception):
  pass
class CoordinatesException(Exception):
  pass

BOARD_ICON_MAP = {
  '0': '_',
  '1': 'x',
  '2': 'o'
}

def is_integer(data):
  try:
    integer = int(data)
    return True
  except Exception as ex:
    return False

def parse_json_response(response):
  str_response = response.read().decode('utf-8')
  return json.loads(str_response)

def call_server(path):
  response = urllib.request.urlopen(url+path)
  return [parse_json_response(response), response]

def print_game_list():
  game_list, _ = call_server('/list')
  for game in game_list:
    print('{} {}'.format(game['id'], game['name']))
  return [gameId['id'] for gameId in game_list]

def connect_to_game(game_id, avaiable_games):
  game_id = int(game_id)
  if game_id not in avaiable_games:
    raise ConnectException('Game does not exist')

  connect_response, _ = call_server('/connect?id={}'.format(game_id))
  if connect_response['status'] == 'bad':
    raise ConnectExcep('Error from server to connect')
  return connect_response

def create_new_game():
  game_name = input('Insert game name:\n')
  start_response, _ = call_server('/start?name={}'.format(game_name))
  return start_response['id']

def get_game_status(game_id):
  status_response, response = call_server('/status?game={}'.format(game_id))
  if response.status >= 400:
    raise ('Error from server to get game status')
  return status_response

def print_game_board(board):
  for row in board:
    output_row = ""
    for column in row:
      output_row += BOARD_ICON_MAP[str(column)]
    print(output_row)

def print_game(game_id):
  game = get_game_status(game_id)
  print_game_board(game['board'])

def get_player_turn(next_id):
  return 2 if next_id == 1 else 1

def make_move(game_id, player, x, y):
  try:
    play_response, response = call_server('/play?game={}&player={}&x={}&y={}'.format(game_id, player, x, y))
  except Exception as err:
    raise PlayException(err)
  if response.status >= 400:
    raise PlayException('Error from server')
  if play_response['status'] == 'bad':
    raise PlayException(play_response['message'])
  return play_response

def get_coordinates(input_text):
  coordinates = input_text.strip().split()
  if len(coordinates) != 2:
    raise CoordinatesException()
  return coordinates

def print_game_result(winner, as_player):
  if winner == 0:
    print('draw')
  elif winner == as_player:
    print('you win')
  else:
    print('you lose')

def play_game(game_id, as_player):
  game = get_game_status(game_id)
  print_wait = True
  while True:
    game = get_game_status(game_id)
    if 'winner' in game:
      break
    if game['next'] == as_player:
      if print_wait:
        print_game(game_id)
        print('waiting for the other player')
        print_wait = False
      game = get_game_status(game_id)
      sleep(1)
    else:
      print_game(game_id)
      input_coordinates = input('your turn ({}):'.format(BOARD_ICON_MAP[str(get_player_turn(game['next']))]))
      try:
        coordinates = get_coordinates(input_coordinates)
        make_move(game_id, as_player, coordinates[0], coordinates[1])
        print_wait = True
      except (PlayException, CoordinatesException) as err:
        print('invalid input')
  print_game(game_id)
  winner = game['winner']
  print_game_result(winner, as_player)

def new_or_connect(avaiable_games):
  user_input = input('Type "new" to start a new game or id to connect to existing game:\n')
  if user_input == 'new':
    new_game_id = create_new_game()
    play_game(new_game_id, 1)
  elif is_integer(user_input):
    try:
      connect_to_game(user_input, avaiable_games)
      play_game(user_input, 2)
    except ConnectException as err:
      print(str(err))
  else:
    print('invalid input')

def main():
  avaiable_games = print_game_list()
  new_or_connect(avaiable_games)

if __name__ == '__main__':
  number_of_arguments = 3;

  if len(sys.argv) != number_of_arguments:
    sys.exit('Wrong number of arguments')

  _, host, port = sys.argv
  url = 'http://{}:{}'.format(host, str(port))
  main()
