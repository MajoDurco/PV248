#!/usr/bin/env python3

import numpy
import sys
import re

from collections import defaultdict

def isSignNegative(sign):
  if sign.strip() is '-':
    return True;
  return False

def getNumber(number):
  if number:
    return int(number)
  return 1

def parseLine(line):
  equalSplit = line.split('=')
  if len(equalSplit) != 2:
    raise ValueError('Missing "=" in equation', line)
  leftSide = equalSplit[0].strip()
  rigthSide = equalSplit[1].strip()
  coeficients_with_sign = re.findall(r'([+-]?)\s?(\d*)([a-z])', leftSide)
  coeficients = {}
  for sign, number, coeficient in coeficients_with_sign:
    int_number = getNumber(number)
    if isSignNegative(sign):
      int_number *= -1 # negate the number
    if coeficient in coeficients:
      coeficients[coeficient] += int_number
    else:
      coeficients[coeficient] = int_number
  return [coeficients, int(rigthSide)]

def main() :
  numberOfArguments = 2;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, equationFile = sys.argv
  leftSideValues = []
  rightSideValues = []
  variables = []
  with open(equationFile) as file:
    lines = file.readlines()
    coeficientsList = []
    for line in lines:
      coeficients, rightValue = parseLine(line)
      rightSideValues.append(rightValue)
      coeficientsList.append(coeficients)

    variables = tuple(set.union(*[ set(coeficients.keys()) for coeficients in coeficientsList]))
    for coeficients in coeficientsList:
      equationCoeficients = []
      for coeficient in variables:
          if coeficient in coeficients:
            equationCoeficients.append(coeficients[coeficient])
          else:
            equationCoeficients.append(0)
      leftSideValues.append(equationCoeficients)
    

    leftSideValuesNumpy = numpy.array(leftSideValues)
    rightSideValuesNumpy = numpy.array(rightSideValues)
    rank = numpy.linalg.matrix_rank(leftSideValuesNumpy)
    augmented = numpy.hstack((leftSideValuesNumpy, numpy.expand_dims(rightSideValues, axis=1)))
    augment_rank = numpy.linalg.matrix_rank(augmented)

    if augment_rank == rank:
      spaceDimension = len(variables) - augment_rank
      if spaceDimension == 0:
        result = numpy.linalg.solve(leftSideValues, rightSideValues)
        solution = []
        for variable, value in sorted(zip(variables, result), key=lambda var_value_pair: var_value_pair[0]):
          solution.append('{} = {}'.format(variable, value))
        print('solution: {}'.format(', '.join(solution)))
      else:
        print('solution space dimension: {}'.format(spaceDimension))
    else:
        print('no solution')

if __name__ == '__main__':
  main()