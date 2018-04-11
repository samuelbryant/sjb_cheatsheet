#!/usr/bin/python3.6
import sys

import sjb.cs.main

if __name__ == '__main__':
  # Set name of script:
  sys.argv[0] = 'sjb-cheatsheet'
  sjb.cs.main.main()
else:
  print('Error: this file should never be imported')
  sys.exit(1)