#!/usr/bin/env python3

import sys
import json
import math
import pandas
import numpy

from datetime import datetime

def getDate(dates_with_excercise):
  return dates_with_excercise.split('/')[0]

def getExcercises(dates_with_excercise):
  return dates_with_excercise.split('/')[1]

def getTableBasedOnMode(table, mode):
  if mode == 'average':
    table.loc['mean'] = table.mean()
    return table.tail(1)
  elif mode.isdigit():
    return table.loc[table['student'] == int(mode)]
  else:
    sys.exit('Argument can only be id or "average"')

def main():
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, csvFile, mode = sys.argv

  root_table = pandas.read_csv(csvFile)
  table = getTableBasedOnMode(root_table, mode)
  table_without_student = table.drop(columns='student')

  exercises_table = table_without_student.rename(columns=getExcercises)
  exercises_table = exercises_table.groupby(axis='columns', level=0).sum()
  exercises_table = exercises_table.reindex(
    sorted(exercises_table.columns), axis='columns'
  )

  result_dict = {
    "mean" : exercises_table.mean(axis='columns').iloc[0],
    "median" : exercises_table.median(axis='columns').iloc[0],
    "passed" : int(exercises_table.astype(bool).sum(axis='columns')),
    "total" : exercises_table.sum(axis='columns').iloc[0]
  }

  start_semester = datetime.strptime("2018-09-17", "%Y-%m-%d").toordinal()
  date_table = table_without_student.rename(columns=getDate)
  date_table = date_table.groupby(by=date_table.columns, axis='columns').sum()
  date_table = date_table.reindex(sorted(date_table.columns), axis='columns')

  cumsum = date_table.cumsum(axis='columns').iloc[0]

  dates = numpy.array([datetime.strptime(x, '%Y-%m-%d').date().toordinal() - start_semester for x in cumsum.index])
  dates = dates[:, numpy.newaxis]
  slope = numpy.linalg.lstsq(dates, cumsum.values, rcond=None)[0]

  result_dict['regression slope'] = slope[0]
  if slope != 0:
    result_dict['date 16'] = str(datetime.fromordinal(start_semester + 16 / slope).date())
    result_dict['date 20'] = str(datetime.fromordinal(start_semester + 20 / slope).date())

  print(json.dumps(result_dict, indent=2, ensure_ascii = False))

if __name__ == '__main__':
  main()