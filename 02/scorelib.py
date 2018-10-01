#!/usr/bin/python3

import re
import sys

def addMatchToDict(key, matches, dict_ref):
  match = matches[0]
  if match:
    dict_ref[key] = match

def extendMatches(key, matches, dict_ref):
  match = matches[0]
  if match:
    if key in dict_ref:
      dict_ref[key].append(match)
    else:
      dict_ref[key] = [match]

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

TRANSLATION_DICT = {
  'printNumber': {
    'regex': re.compile('Print Number:\s*(\d+)'),
    'translation': addMatchToDict,
    'output': 'Print Number: {0}',
  },
  'composers': {
    'regex': re.compile('Composer:\s*(.*)'),
    'translation': (lambda *args: addSeparatedMatches(';', *args)),
    'output': 'Composer: {0}'
  },
  'composition_years': {
    'regex': re.compile('Composition Year:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Composition Year: {0}',
  },
  'partiture': {
    'regex': re.compile('Partiture:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Partiture: {0}',
  },
  'edition': {
    'regex': re.compile('Edition:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Edition: {0}',
  },
  'editor': {
    'regex': re.compile('Editor:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Edition: {0}',
  },
  'title': {
    'regex': re.compile('Title:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Title: {0}',
  },
  'incipit': {
    'regex': re.compile('Incipit:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Incipit: {0}',
  },
  'key': {
    'regex': re.compile('Key:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Key: {0}',
  },
  'genre': {
    'regex': re.compile('Genre:\s*(.*)'),
    'translation': addMatchToDict,
    'output': 'Genre: {0}',
  },
  'voices': {
    'regex': re.compile('Voice \d+:\s*(.*)'),
    'translation': (lambda key, *args: extendMatches('voices', *args)),
    'output': 'Voice: {0}',
  }
}

def load(filename):
  with open(filename) as file:
    fileContent = file.readlines()

  translatedList = []
  translatedDict = {}
  for line in fileContent:
    stripped_line = line.strip()
    if not stripped_line:
      if translatedDict: 
        # for empty string translatedDict can be {}, 
        # dont want to process that
        translatedList.append(Print(translatedDict))
      translatedDict = {}
    for key, value in TRANSLATION_DICT.items():
      match = value['regex'].match(stripped_line)
      if match:
        value['translation'](key, list(match.groups()), translatedDict)
  translatedList.append(Print(translatedDict)) # add last record

def getPartiture(partiture):
  if partiture.strip() == 'yes':
    return True
  else:
    return False

class Print:
  def __init__(self, translatedDict):
    self.translatedDict = translatedDict
    self.partiture = getPartiture(translatedDict.get('partiture', ''))
    self.print_id = int(translatedDict.get('printNumber'));
    self.edition = Edition(
      translatedDict
    );

  def format(self):
    for key, value in TRANSLATION_DICT.items():
      print(value.get('output').format(self.translatedDict.get(key, '')))
    print('')
  
  def composition():
    return self.edition.composition()

# has author
class Edition:
  def __init__(self, translatedDict):
    self.composition = Composition(translatedDict)
    self.authors = [ Person(person.strip(', '))
      for person in self.parseEditors(translatedDict.get('editor', ''))
    ]
    self.name = translatedDict.get('edition', None)

  def parseEditors(self, editors):
    if not ',' in editors:
      parsedEditors = re.findall(r'([^\s]+\s*[^\s]+)', editors)
    else:
      parsedEditors = re.findall(r'([^\s]+,\s*[^\s]+)', editors)
    return parsedEditors

class Composition:
  def __init__(self, translatedDict):
    self.name = translatedDict.get('title', None)
    self.incipit = translatedDict.get('incipit', None)
    self.key = translatedDict.get('key', None)
    self.genre = translatedDict.get('genre', None)
    self.year = self.parseCompositionYear(translatedDict.get('composition_years', ''))
    self.voices = [Voice(voice) for voice in translatedDict.get('voices', [])]
    self.authors = self.parseComposers(translatedDict.get('composers', []))
    print('self.authors', self.authors)

  def __repr__(self):
    return 'Composition: name: {}, incipit: {}, key: {}, genre: {}, year: {}'.format(
      self.name, self.incipit, self.key, self.genre, self.year
    )
  
  def parseCompositionYear(self, composition_year):
    year = re.match(r'.*(\d{4}).*', composition_year)
    if year:
      return int(year.group(1))
    else:
      return None
  
  def parseComposers(self, composers):
    personComposers = []
    for composer in composers:
      print('composer', composer)
      composerMatch= re.match(r'([^\(]+)(\(.*\))?', composer)
      if composerMatch:
        name = composerMatch.group(1)
        date = re.match(r'\(\*?([\d\/]+)?-{0,2}\+?(.*?)?\)', composerMatch.group(2))
        born = None
        died = None
        if date:
          bornDate = date.group(1)
          if bornDate:
            bornDateMatch = re.match(r'(^\d{4}$)', bornDate)
            if bornDateMatch:
              born = bornDateMatch.group(1)
          diedDate = date.group(2)
          if diedDate:
            diedDateMatch = re.match(r'(^\d{4}$)', diedDate)
            if diedDateMatch:
              died = diedDateMatch.group(1)
          personComposers.append(Person(name, born, died))
        else:
          personComposers.append(Person(nam + composerMatch.group(2)))
    print('personComposers', personComposers)
    return personComposers

class Voice:
  def __init__(self, voice):
    voice_match = re.match(r'(.+--[^\s|,]+)?,?\s?(.*)', voice)
    if voice_match:
      self.range = voice_match.group(1)
      self.name = voice_match.group(2)
    else:
      self.name = ''
      self.range = None
  
  def __repr__(self):
    return 'Voice: name: {}, range: {}'.format(self.name, self.range)

# editor, composer, autor are Persons(instances)
class Person:
  def __init__(self, name='', born=None, died=None):
    self.name = name
    self.born = born
    self.died = died
  
  def __repr__(self):
    return 'Person {}, {} -- {}'.format(self.name, self.born, self.died)
  
_, textFile = sys.argv
load(textFile)
