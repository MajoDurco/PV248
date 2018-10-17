#!/usr/bin/python3

import sys
import sqlite3
import json

def logTable(cursor, name):
  print(name.upper())
  for row in cursor.execute("SELECT * from {}".format(name)): # DANGEROUS ony for debug
    print(row)

def falsyToNull(value):
  if value == 'NULL' or not value:
    return 'null'
  return value

def parseComposers(composers):
  return [{
    'name': falsyToNull(composer[0]),
    'born': falsyToNull(composer[1]),
    'died': falsyToNull(composer[2])
  } for composer in composers]

def main():
  if len(sys.argv) != 2:
    sys.exit('Wrong program arguments')

  _, composer_name = sys.argv

  connect = sqlite3.connect('scorelib.dat')
  cursor = connect.cursor()

  logTable(cursor, 'person')
  print('####################')

  cursor.execute('''
    SELECT * FROM (SELECT * FROM person WHERE person.name LIKE ?) JOIN 
  ''', ("%" + composer_name + "%",))
  for row in cursor.fetchall():
    print(row)
        # JOIN edition ON print.edition = edition.id
        # JOIN score ON edition.score = score.id
        # JOIN score_author ON score.id = score_author.score
        # JOIN person ON person.id = score_author.composer
  cursor.close()

if __name__ == '__main__':
  main()