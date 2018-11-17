#!/usr/bin/env python3

import sys
import json
import pandas

def getDate(dates_with_excercise):
  return dates_with_excercise.split('/')[0]

def getExcercises(dates_with_excercise):
  return dates_with_excercise.split('/')[1]

def getTableBasedOnMode(table, mode):
  if mode == 'dates':
    return table.rename(columns=getDate)
  elif mode == 'excercises':
    return table.rename(columns=getExcercises)
  elif mode == 'deadlines':
    return table
  else:
    sys.exit('Wrong mode')

def main():
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, csvFile, mode = sys.argv
  
  table = pandas.read_csv(csvFile)
  table.drop(columns='student', inplace=True)
  table = getTableBasedOnMode(table, mode)

  result_table = pandas.concat([
    table.mean(),
    table.median(),
    table.quantile(.25),
    table.quantile(.75),
    int(table.astype(bool).sum())
  ], axis='columns')
  result_table.columns = ['mean', 'median', 'first', 'last', 'passed']
  
  print(json.dumps(result_table.to_dict(orient="index"), indent=2, ensure_ascii = False))

if __name__ == '__main__':
  main()