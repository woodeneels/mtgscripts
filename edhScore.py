#! python3
# edhScore.py - Pulls a general from edhrec.com/local decklist and scores vs inventory csv.

import requests, bs4, re, csv, os, sys, argparse, html5lib

# --- define functions ---
def importColl():
    # set up collection
    print('Importing inventory...')
    collection = []
    if not os.path.isfile('inventory.csv'):
        print('[ERROR] File not found: inventory.csv. Please make sure your'
              + ' inventory.csv file is in the same directory as this script.'
              + '\nIf you do not have an inventory.csv, you can export one'
              + ' from deckbox.org (make sure you rename it to inventory.csv)')
        exit()
    invFile = open('inventory.csv')
    invReader = csv.reader(invFile)

    for row in invReader:
        if len(row) == 0:
            break
        collection.append(row[2])
        
    return collection

def getRandom():
    # get general
    print('Getting random general...')

    res = requests.get('https://edhrec.com/random/')
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, 'html5lib')
    general = soup.select('.panel-title')[0].getText()
    genLinks = soup.select('div > p > a')
    deckLink = genLinks[1].get('href')

    # get decklist
    print('Getting average decklist...')
    res = requests.get('https://edhrec.com' + deckLink)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, 'html5lib')
    deckString = str(soup.select('.well'))
    deckRegex = re.compile(r'>(\d.+?(?=<))')
    deckList = deckRegex.findall(deckString)
    
    return general, deckList

def getSpecific(general):
    # check general
    print('Searching for general: ' + general)
    genFormatted = re.sub(r'[^a-zA-Z0-9 ]+', '', general)
    genFormatted = str.replace(genFormatted, ' ', '-').lower()

    res = requests.get('https://edhrec.com/decks/' + genFormatted)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, 'html5lib')
    deckString = str(soup.select('.well'))
    deckRegex = re.compile(r'>(\d.+?(?=<))')
    deckList = deckRegex.findall(deckString)
    
    return deckList

def printInfo(collection, general, deckList):
    # print out general
    print()
    print('Your general is: ' + general)
    print()
    
    # include general in card list for easy importing
    print('1 ' + general)

    # print out decklist
    for i in deckList:
        print(i)

    # score deck completion vs collection
    score = 0
    scoreposs = 1 # general not in decklist

    if general in deckList:
        score += 1

    for i in deckList:
        if i.startswith('1 '): # if a single (i.e. non-basic land) card in the list
            scoreposs += 1
            if i[2:] in collection:
                score += 1

    print()
    print('Score: ' + str(score) + ' of a possible ' + str(scoreposs)
          + ' (' + str(round((score / scoreposs) * 100)) + '%)')
    
    return

# --- start program ---
# set up argument parser
parser = argparse.ArgumentParser(description='edhScore.py - Pulls a general from edhrec.com/local decklist and scores vs inventory csv.')
parser.add_argument('-g','--general',help='General name e.g. "Jalira, Master Polymorphist"',default='empty',required=False)
parser.add_argument('-l','--decklist',help='Relative path to decklist e.g. "decklists/edric-flying-men.txt"',default='empty',required=False)
args = parser.parse_args()

if (args.general is not 'empty'):
    # handle general
    collection = importColl()
    deckList = getSpecific(args.general)
    printInfo(collection, args.general, deckList)
elif (args.decklist is not 'empty'):
    # handle decklist
    print('decklist: mode not implemented yet')
else:
    # random general
    collection = importColl()
    general, deckList = getRandom()
    printInfo(collection, general, deckList)
