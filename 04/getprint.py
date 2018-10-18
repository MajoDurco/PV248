#!/usr/bin/python3

import sys
import sqlite3
import json

def logTable(cursor, name):
  print(name.upper())
  for row in cursor.execute("SELECT * from {}".format(name)): # DANGEROUS ony for debug
    print(row)

def falsyToNone(value):
  if value == 'NULL' or not value:
    return None
  return value

def parseComposers(composers):
  return [{
    'name': falsyToNone(composer[0]),
    'born': falsyToNone(composer[1]),
    'died': falsyToNone(composer[2])
  } for composer in composers]

def main():
  if len(sys.argv) != 2:
    sys.exit('Wrong program arguments')

  _, print_id = sys.argv

  connect = sqlite3.connect('scorelib.dat')
  cursor = connect.cursor()

  cursor.execute('''
    SELECT person.name, person.born, person.died FROM
      (SELECT * FROM print WHERE id = ?) print 
        JOIN edition ON print.edition = edition.id
        JOIN score ON edition.score = score.id
        JOIN score_author ON score.id = score_author.score
        JOIN person ON person.id = score_author.composer
  ''', (int(print_id),))
  parsed_composers = parseComposers(cursor.fetchall())
  print(json.dumps(parsed_composers, indent=2, ensure_ascii=False))

  cursor.close()
 
if __name__ == '__main__':
  main()
