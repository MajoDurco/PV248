#!/usr/bin/python3

import re

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

def stringValueOutput(string, value):
  print(string.format(value))

def listValueOutput(string, values, separator=''):
  print(string, end='')
  for i in range(len(values)):
    if i == len(values)-1: #last element
      print(values[i])
    else:
      print(values[i], end=separator)

def outputVoice():
  pass

TRANSLATION_DICT = {
  'printNumber': {
    'regex': re.compile('Print Number:\s*(\d+)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Print Number: {}', value)),
  },
  'composers': {
    'regex': re.compile('Composer:\s*(.*)'),
    'translation': (lambda *args: addSeparatedMatches(';', *args)),
    'output': (lambda values: listValueOutput('Composer: ', values, '; ')),
  },
  'title': {
    'regex': re.compile('Title:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Title: {}', value)),
  },
  'genre': {
    'regex': re.compile('Genre:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Genre: {}', value)),
  },
  'key': {
    'regex': re.compile('Key:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Key: {}', value)),
  },
  'composition_years': {
    'regex': re.compile('Composition Year:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Composition Year: {}', value)),
  },
  'edition': {
    'regex': re.compile('Edition:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Edition: {}', value)),
  },
  'editor': {
    'regex': re.compile('Editor:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Editor: {}', value)),
  },
  'voices': {
    'regex': re.compile('Voice \d+:\s*(.*)'),
    'translation': (lambda key, *args: extendMatches('voices', *args)),
    'output': (lambda values: listValueOutput('Voice: ', values, ', ')),
  },
  'partiture': {
    'regex': re.compile('Partiture:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Partiture: {}', value)),
  },
  'incipit': {
    'regex': re.compile('Incipit:\s*(.*)'),
    'translation': addMatchToDict,
    'output': (lambda value: stringValueOutput('Incipit: {}', value)),
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
  sortedTranslatedList = sorted(translatedList, key=lambda printInstance: printInstance.print_id)
  return sortedTranslatedList

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
  
  def __repr__(self):
    return 'Print:\n partiture: {}\n printId: {}\n edition: {}\n'.format(
      self.partiture, self.print_id, self.edition
    )

  def format(self):
    for key, value in TRANSLATION_DICT.items():
      value.get('output')(self.translatedDict.get(key, ''))
  
  def composition():
    return self.edition.composition()

class Edition:
  def __init__(self, translatedDict):
    self.composition = Composition(translatedDict)
    self.authors = [ Person(person.strip(', '))
      for person in self.parseEditors(translatedDict.get('editor', ''))
    ]
    self.name = translatedDict.get('edition', None)
  
  def __repr__(self):
    return 'Edition:\n composition: {}\n Editors: {}\n name: {}\n'.format(
      self.composition, self.authors, self.name
    )

  def parseEditors(self, editors):
    if not ',' in editors:
      parsedEditors = re.findall(r'([^\s]+\s*[^\s]+)', editors)
    else:
      parsedEditors = re.findall(r'([^\s]+,\s*[^\s]+)', editors)
    return parsedEditors

class Composition:
  def __init__(self, translatedDict):
    self.name = translatedDict.get('title', None)
    self.incipit = self.parseIncipit(translatedDict.get('incipit', None))
    self.key = translatedDict.get('key', None)
    self.genre = translatedDict.get('genre', None)
    self.year = self.parseCompositionYear(translatedDict.get('composition_years', ''))
    self.voices = [Voice(voice) for voice in translatedDict.get('voices', [])]
    self.authors = self.parseComposers(translatedDict.get('composers', []))

  def __repr__(self):
    return 'Composition:\n name: {}\n incipit: {}\n key: {}\n genre: {}\n year: {}\n voices: {}\n authors: {}\n'.format(
      self.name, self.incipit, self.key, self.genre, self.year, self.voices, self.authors
    )
  
  def parseIncipit(self, incipit):
    if incipit:
      incipits = incipit.split('|')
      if len(incipits) > 1:
        return incipits[0]
    else:
      return None

  def parseCompositionYear(self, composition_year):
    year = re.match(r'.*(\d{4}).*', composition_year)
    if year:
      return int(year.group(1))
    else:
      return None
  
  def parseComposers(self, composers):
    personComposers = []
    for composer in composers:
      composerMatch= re.match(r'([^\(]+)(\(.*\))?', composer)
      if composerMatch:
        name = composerMatch.group(1)
        dateMatch = composerMatch.group(2)
        if dateMatch:
          date = re.match(r'\(\*?\s*([\d\/]+)?\s*-{0,2}\s*\+?\s*(.*?)?\)', dateMatch)
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
            personComposers.append(Person(name + dateMatch))
        else:
          personComposers.append(Person(name))
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

class Person:
  def __init__(self, name='', born=None, died=None):
    self.name = name
    self.born = born
    self.died = died
  
  def __repr__(self):
    return 'Person {}, {} -- {}'.format(self.name, self.born, self.died)