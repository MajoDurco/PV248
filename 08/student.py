#!/usr/bin/env python3

import sys

def main():
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, csvFile, student_id = sys.argv

if __name__ == '__main__':
  main()