#! python3
# deckboxParseNotOwned.py - parses the contents of the clipboard into a usable card list.
#                           hit "buy not owned" on a deckbox list and copy the list to the clipboard,
#                           then run this script to print out a list that can be imported into e.g. mcm.

import pyperclip, re

listRegex = re.compile(r'\t(\d{0,}\t.+?(?=\t))')

# find matches
cards = str(pyperclip.paste())
mo = listRegex.search(cards)
matches = ''
count = 0
for group in listRegex.findall(cards):
    matches += group.replace('\t', ' ') + '\n'
    count += 1

pyperclip.copy(matches)
print('Copied ' + str(count) + ' lines to clipboard.')
