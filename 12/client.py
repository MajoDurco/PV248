#!/usr/bin/env python3

import sys
import json
import urllib.request

class ConnectException(Exception):
  pass
class StatusException(Exception):
  pass

def is_integer(data):
  try:
    integer = int(data)
    return True
  except Exception as ex:
    return False

def parse_json_response(response):
  try:
    str_response = response.read().decode('utf-8')
    return json.loads(str_response)
  except Exception as e: # TODO make specific
    print(e)
    return None

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

def new_or_connect(avaiable_games):
  user_input = input('Type "new" to start a new game or id of a existing game to connect to it:\n')
  if user_input == 'new':
    new_game_id = create_new_game()
    print('status:', get_game_status(new_game_id))
  elif is_integer(user_input):
    try:
      connect_to_game(user_input, avaiable_games)
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
