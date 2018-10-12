#!/usr/bin/python3

import sqlite3
import sys
from scorelib import load

_, dataFile, datFile = sys.argv

parsedData = load(dataFile)
conn = sqlite3.connect(datFile)
cursor = conn.cursor()
for data in parsedData:
  editors = data.edition.authors
  # print([editor.getToupleData() for editor in editors])
  cursor.executemany("INSERT INTO person VALUES (NULL, ?,?,?)", [editor.getToupleData() for editor in editors])

for person in cursor.execute('SELECT * from person'):
  print(person)

# conn.commit()
conn.close()