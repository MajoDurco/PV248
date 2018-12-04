#!/usr/bin/env python3

print('PYTHON script')
with open('tfjkadfjald.txt', 'w+') as file:
  for i in range(10):
    file.write("This is line %d\r\n" % (i+1))