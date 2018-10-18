#!/usr/bin/python3

import sys
import sqlite3
import json

def falsyToNone(value):
  if value == "NULL" or not value:
    return None
  return value

def parseSearchResult(cursor):
  result_dic = {}
  for row in cursor.fetchall():
    person_data_dic = {}

    person_data_dic["Print Number"] = row[1]

    cursor.execute("SELECT person.name, person.born, person.died from score_author JOIN person ON score_author.composer = person.id WHERE score_author.score = ?", (row[2],))
    person_data_dic["Composers"] = [
      {
        "name": composer[0],
        "born": falsyToNone(composer[1]),
        "died": falsyToNone(composer[2]),
      } for composer in cursor.fetchall()
    ]
    person_data_dic["Title"] = falsyToNone(row[3])
    person_data_dic["Genre"] = falsyToNone(row[4])
    person_data_dic["Key"] = falsyToNone(row[5])
    person_data_dic["Composition Year"] = falsyToNone(row[6])
    person_data_dic["Edition"] = falsyToNone(row[7])

    cursor.execute("SELECT person.name, person.born, person.died from edition_author JOIN person ON edition_author.editor = person.id WHERE edition_author.edition = ?", (row[8],))
    person_data_dic["Editors"] = [
      {
        "name": composer[0],
        "born": falsyToNone(composer[1]),
        "died": falsyToNone(composer[2]),
      } for composer in cursor.fetchall()
    ]

    cursor.execute("SELECT voice.number, voice.name, voice.range from voice JOIN score ON voice.score = score.id WHERE score.id = ?", (row[2],))
    person_data_dic["Voices"] = {
      voice[0]:{
        "name": falsyToNone(voice[1]),
        "range": falsyToNone(voice[2])
      } for voice in cursor.fetchall()
    }
    person_data_dic["Partiture"] = falsyToNone(row[9])
    person_data_dic["Incipit"] = falsyToNone(row[10])

    person_name = row[0]
    result_dic[person_name] = [person_data_dic]
  return result_dic

def main():
  if len(sys.argv) != 2:
    sys.exit('Wrong program arguments')

  _, composer_name = sys.argv

  connect = sqlite3.connect('scorelib.dat')
  cursor = connect.cursor()

  cursor.execute('''
    SELECT
    person.name, print.id, score.id,
    score.name, score.genre, score.key,
    score.year, edition.name, edition.id,
    print.partiture, score.incipit
      FROM (SELECT * FROM person WHERE person.name LIKE ?) person
        JOIN score_author s_a ON person.id = s_a.composer
        JOIN score ON score.id = s_a.score
        JOIN voice ON voice.score = score.id
        JOIN edition ON edition.score = score.id
        JOIN print ON print.edition = edition.id
  ''', ("%" + composer_name + "%",))

  result = parseSearchResult(cursor)

  print(json.dumps(result, indent=2, ensure_ascii=False))
  cursor.close()

if __name__ == '__main__':
  main()