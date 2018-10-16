#!/usr/bin/python3

import sqlite3
import sys
from scorelib import load

def saveData(parsedScores, cursor):
  for score in parsedScores:

    savedEditorIds = []
    # EDITORS
    for editor in score.edition.authors:
      toupleData = editor.getToupleData()
      cursor.execute("SELECT * FROM person WHERE name = ?", (toupleData[2],))
      selectedEditor = cursor.fetchone()
      if selectedEditor is None:
        cursor.execute("INSERT INTO person VALUES (NULL, ?,?,?)", toupleData)
        savedEditorIds.append(cursor.lastrowid)
      else:
        if toupleData[0] is not 'NULL':
          cursor.execute("UPDATE person SET born = ? WHERE id = ?", (toupleData[0], selectedEditor[0]))
        if toupleData[1] is not 'NULL':
          cursor.execute("UPDATE person SET died = ? WHERE id = ?", (toupleData[1], selectedEditor[0]))
        savedEditorIds.append(selectedEditor[0])

    savedComposerIds = []
    # COMPOSERS
    for composer in score.edition.composition.authors:
      toupleData = composer.getToupleData()
      cursor.execute("SELECT * FROM person WHERE name = ?", (toupleData[2],))
      selectedComposer = cursor.fetchone()
      if selectedComposer is None:
        cursor.execute("INSERT INTO person VALUES (NULL, ?,?,?)", toupleData)
        savedComposerIds.append(cursor.lastrowid)
      else:
        if toupleData[0] is not 'NULL':
          cursor.execute("UPDATE person SET born = ? WHERE id = ?", (toupleData[0], selectedComposer[0]))
        if toupleData[1] is not 'NULL':
          cursor.execute("UPDATE person SET died = ? WHERE id = ?", (toupleData[1], selectedComposer[0]))
        savedComposerIds.append(selectedComposer[0])

    # COMPOSITION
    toupleData = score.edition.composition.getToupleData()
    cursor.execute("SELECT * from score WHERE name = ? AND genre = ? AND key = ? AND incipit = ? AND year = ?", toupleData)
    create_new_composition = True
    all_same_scores = cursor.fetchall()
    for same_score in all_same_scores:
      composers_are_same = False
      voices_are_same = False
      cursor.execute("SELECT sa.composer from score_author sa NATURAL JOIN person WHERE score = ?", (same_score[0],))
      foundCompositionAuthorIds = [ composer[0] for composer in cursor.fetchall() ]
      if foundCompositionAuthorIds == savedComposerIds:
        composers_are_same = True

      cursor.execute("SELECT * from voice WHERE score = ?", (same_score[0],))
      existing_voices = [ (str(voice[1]), voice[3], voice[4]) for voice in cursor.fetchall() ]
      new_voices = [ (voice.getToupleData(same_score[0])[0], voice.getToupleData(same_score[0])[2], voice.getToupleData(same_score[0])[3]) for voice in score.edition.composition.voices ]
      if existing_voices == new_voices:
        voices_are_same = True

      if composers_are_same and voices_are_same:
        create_new_composition = False
        compositionId = same_score[0]
        break

    if create_new_composition:
      cursor.execute("INSERT INTO score VALUES (NULL, ?,?,?,?,?)", toupleData)
      compositionId = cursor.lastrowid

    # VOICE
    for voice in score.edition.composition.voices:
      toupleData = voice.getToupleData(compositionId)
      cursor.execute("SELECT number, score, range, name from voice where number = ? AND score = ? AND range = ? AND name = ?", toupleData)
      if cursor.fetchone() == None:
        cursor.execute("INSERT INTO voice VALUES (NULL, ?,?,?,?)", toupleData)

    # EDITION
    toupleData = score.edition.getToupleData(compositionId)
    cursor.execute("SELECT * from edition where score = ? AND name = ?", (toupleData[:2]))
    found_edition = cursor.fetchone()
    editors_are_same = False
    create_new_edition = True
    if found_edition is not None:
      cursor.execute("SELECT ea.editor from edition_author ea NATURAL JOIN person WHERE edition = ?", (found_edition[0],))
      foundEditionAuthorsIds = [ editor[0] for editor in cursor.fetchall() ]
      if foundEditionAuthorsIds == savedEditorIds:
        editors_are_same = True
      editionId = found_edition[0]
      if editors_are_same:
        create_new_edition = False
        editionId = found_edition[0]
        break

    if create_new_edition:
      cursor.execute("INSERT INTO edition VALUES (NULL, ?,?,?)", toupleData)
      editionId = cursor.lastrowid

    # COMPOSITION - AUTHOR (COMPOSERS)
    for composerId in savedComposerIds:
      cursor.execute("SELECT * from score_author WHERE score = ? AND composer = ?", (compositionId, composerId))
      if cursor.fetchone() is None:
        cursor.execute("INSERT INTO score_author VALUES (NULL, ?,?)", (compositionId, composerId))

    # EDITION - AUTHOR (EDITORS)
    for editorId in savedEditorIds:
      cursor.execute("SELECT * from edition_author WHERE edition = ? AND editor = ?", (editionId, editorId))
      if cursor.fetchone() is None:
        cursor.execute("INSERT INTO edition_author VALUES (NULL, ?,?)", (editionId, editorId))

    # PRINT
    toupleData = score.getToupleData(editionId)
    cursor.execute("SELECT * from print WHERE id = ? AND partiture = ? AND edition = ?", (toupleData[0], toupleData[1], editionId))
    if cursor.fetchone() is None:
      cursor.execute("INSERT INTO print VALUES (?,?,?)", toupleData)

def logTable(cursor, name):
  print(name.upper())
  for row in cursor.execute("SELECT * from {}".format(name)): # REMOVE DANGEROUS
    print(row)

def main():
  if len(sys.argv) != 3:
    sys.exit('Wrong program arguments')

  _, dataFile, datFile = sys.argv

  conn = sqlite3.connect(datFile)
  cursor = conn.cursor()

  try:
    with open('scorelib.sql') as sql_file:
      cursor.executescript(sql_file.read())
  except sqlite3.OperationalError:
    pass
  
  saveData(load(dataFile), cursor)

  # logTable(cursor, 'person')
  # logTable(cursor, 'score')
  # logTable(cursor, 'voice')
  # logTable(cursor, 'edition')
  # logTable(cursor, 'score_author')
  # logTable(cursor, 'edition_author')
  # logTable(cursor, 'print')
  conn.commit()
  conn.close()

if __name__ == '__main__':
  main()
