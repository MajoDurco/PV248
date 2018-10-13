#!/usr/bin/python3

import sqlite3
import sys
from scorelib import load

_, dataFile, datFile = sys.argv

parsedScores = load(dataFile)
conn = sqlite3.connect(datFile)
cursor = conn.cursor()
for score in parsedScores:
  savedEditorIds = []
  # EDITORS
  for editor in score.edition.authors:
    toupleData = editor.getToupleData()
    cursor.execute("SELECT * FROM person WHERE born = ? AND died = ? AND name = ?", toupleData)
    if cursor.fetchone() is None:
      cursor.execute("INSERT INTO person VALUES (NULL, ?,?,?)", toupleData)
      savedEditorIds.append(cursor.lastrowid)

  savedComposerIds = []
  # COMPOSERS
  for composer in score.edition.composition.authors:
    toupleData = composer.getToupleData()
    cursor.execute("SELECT * FROM person WHERE born = ? AND died = ? AND name = ?", toupleData)
    if cursor.fetchone() is None:
      cursor.execute("INSERT INTO person VALUES (NULL, ?,?,?)", toupleData)
      savedComposerIds.append(cursor.lastrowid)

  # COMPOSITION
  toupleData = score.edition.composition.getToupleData()
  cursor.execute("INSERT INTO score VALUES (NULL, ?,?,?,?,?)", toupleData)
  compositionId = cursor.lastrowid

  # VOICE
  for voice in score.edition.composition.voices:
    toupleData = voice.getToupleData(compositionId)
    # Don't save the same voice in composition
    # Ex:
    # Voice 1: piano
    # Voice 1: piano
    # Should be saved only once
    cursor.execute("SELECT number, score, range, name from voice where number = ? AND score = ? AND range = ? AND name = ?", toupleData)
    if cursor.fetchone() == None:
      cursor.execute("INSERT INTO voice VALUES (NULL, ?,?,?,?)", toupleData)

  composition_voices_grouped_by_compositionId = {}
  cursor.execute("SELECT score.id, score.name, score.genre, score.key, score.incipit, score.year, voice.number, voice.range, voice.name from score join voice on score.id = voice.score")
  join_result = cursor.fetchall()
  # Group by score id
  for result in join_result:
    score_id = result[0]
    if score_id in composition_voices_grouped_by_compositionId:
      composition_voices_grouped_by_compositionId[score_id].append(result[1: ])
    else:
      composition_voices_grouped_by_compositionId[score_id] = [result[1: ]]
  print(composition_voices_grouped_by_compositionId)
  last_voices = composition_voices_grouped_by_compositionId.pop(compositionId)
  if last_voices in composition_voices_grouped_by_compositionId.values():
    print('delete')
    cursor.execute("DELETE FROM voice WHERE score == ?", (compositionId,))
    cursor.execute("DELETE FROM score WHERE id = ?", (compositionId,))

  print('')
  # EDITION
  toupleData = score.edition.getToupleData(compositionId)
  cursor.execute("INSERT INTO edition VALUES (NULL, ?,?,?)", toupleData)
  editionId = cursor.lastrowid

  # COMPOSITION - AUTHOR (COMPOSERS)
  for composerId in savedComposerIds:
    cursor.execute("INSERT INTO score_author VALUES (NULL, ?,?)", (compositionId, composerId))

  # EDITION - AUTHOR (EDITORS)
  for editorId in savedEditorIds:
    cursor.execute("INSERT INTO edition_author VALUES (NULL, ?,?)", (editionId, editorId))

  # PRINT
  toupleData = score.getToupleData(editionId)
  cursor.execute("INSERT INTO print VALUES (?,?,?)", toupleData)

def logTable(cursor, name):
  print(name.upper())
  for row in cursor.execute("SELECT * from {}".format(name)): # REMOVE DANGEROUS
    print(row)


print("")
print("DATABASE")
print("")
logTable(cursor, 'person')
logTable(cursor, 'score')
logTable(cursor, 'voice')
logTable(cursor, 'score_author')
logTable(cursor, 'edition_author')
logTable(cursor, 'print')

# conn.commit()
conn.close()