#!/usr/bin/python3

import re
import sys

def addMatchToDict(key, matches, dict_ref):
  match = matches[0]
  if match:
    dict_ref[key] = match

def addMultipleMatches(key, matches, dict_ref):
  dict_ref[key] = [ match for match in matches if match ];

def addSeparatedMatches(separator, key, matches, dict_ref):
  splited_matches = [ match.strip() for match in matches[0].split(separator)]
  if splited_matches:
    addMultipleMatches(key, splited_matches, dict_ref)

def removeParenthesisFromMatch(separator, key, matches, dict_ref):
  splited_matches = [
    re.sub(r'\s*\(.*\)\s*', '', match).strip()
    for match in matches[0].split(separator)
  ]
  if splited_matches:
    addMultipleMatches(key, splited_matches, dict_ref)

def countComposers(compositions):
  composers = {}
  for composition in compositions:
    for composer in composition.get('composers', []):
      if composer in composers:
        composers[composer] += 1
      else:
        composers[composer] = 1
  return composers

translationDict = {
  'printNumber': {
    'default': None,
    'regex': re.compile('Print Number:\s*(\d+)'),
    'translation': addMatchToDict,
  },
  'composers': {
    'default': [],
    'regex': re.compile('Composer:\s*(.*)'),
    'translation': (lambda *args: removeParenthesisFromMatch(';', *args)),
  },
  'composition_year': {
    'default': [],
    'regex': re.compile('Composition Year:\s*(.*)'),
    'translation': (lambda *args: addSeparatedMatches(',', *args)),
  },
}

def main(*args, **kwargs):
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, textFile, outputType = sys.argv

  with open(outputType) as file:
    fileContent = file.readlines()

  translatedList = []
  translatedDict = {}
  for line in fileContent:
    stripped_line = line.strip()
    if not stripped_line:
      translatedList.append(translatedDict)
      translatedDict = {}
    for key, value in translationDict.items():
      match = value['regex'].match(stripped_line)
      if match:
        value['translation'](key, list(match.groups()), translatedDict)
  translatedList.append(translatedDict) # add last record


  import pprint
  pprint.pprint(translatedList)
  pprint.pprint(countComposers(translatedList))
  # print('###########')

if __name__ == "__main__":
  main()
