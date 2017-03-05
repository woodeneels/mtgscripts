#! python3
# edhRandGen.py - Pulls a random general from edhrec.com.

import requests, bs4, re

# get general
print('Getting random general...')

res = requests.get('https://edhrec.com/random/')
res.raise_for_status()

soup = bs4.BeautifulSoup(res.text, 'html.parser')
general = soup.select('.panel-title')[0].getText()
genLinks = soup.select('div > p > a')
deckLink = genLinks[1].get('href')
print('Your general is: ' + general)
print()

# get decklist
print('Getting average decklist...')
res = requests.get('https://edhrec.com' + deckLink)
res.raise_for_status()

soup = bs4.BeautifulSoup(res.text, 'html.parser')
deckString = str(soup.select('.well'))
deckRegex = re.compile(r'>(\d.+?(?=<))')
deckList = deckRegex.findall(deckString)
for i in deckList:
    print(i)
