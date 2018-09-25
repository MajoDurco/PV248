#!/usr/bin/python3

import re
import sys
import pprint

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

def getCenturyFromCompositionYear(year):
  matchYear = re.match(r'.*(\d{4}).*', year)
  matchCentury = re.match(r'.*(\d{2})th.*', year)
  if matchYear:
    return ((int(matchYear.group(1))) - 1) // 100 + 1
  elif matchCentury:
    return (int(matchCentury.group(1)))
  else:
    return False

def countCompositionPerCentury(compositions):
  centuries = {}
  for composition in compositions:
    for year in composition.get('composition_years', []):
      century = getCenturyFromCompositionYear(year)
      if century:
        if century in centuries:
          centuries[century] += 1
        else:
          centuries[century] = 1
  return centuries

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
  'composition_years': {
    'default': [],
    'regex': re.compile('Composition Year:\s*(.*)'),
    'translation': (lambda *args: addSeparatedMatches(',', *args)),
  },
}

def main(*args, **kwargs):
  numberOfArguments = 3;
  outputTypes = ['composer', 'century']

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, textFile, outputType = sys.argv
  if outputType not in outputTypes:
    sys.exit(str.format('Wrong second argument accepted are: {0}', ', '.join(outputTypes)))

  with open(textFile) as file:
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

  if outputType == 'composer':
    countedComposers = countComposers(translatedList)
    for composer, count in countedComposers.items():
      print('{0}: {1}'.format(composer, count))
  elif outputType == 'century':
    countedCenturies = countCompositionPerCentury(translatedList)
    for century, count in countedCenturies.items():
      print('{0}th century: {1}'.format(century, count))

if __name__ == "__main__":
  main()
