#! python3
# csvParseTest.py - Parses a given csv list of cards and prints unique entries.

import csv

invFile = open('inventory.csv')
invReader = csv.reader(invFile)

for row in invReader:
    if len(row) == 0:
        break
    print(row[2])
