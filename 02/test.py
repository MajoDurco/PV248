#!/usr/bin/python3

import sys

from scorelib import load

_, textFile = sys.argv

compositions = load(textFile)
for composition in compositions:
  format(composition.format())
  print()