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
    res = requests.get('https://edhrec.com/random/')
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, 'html5lib')
    general = soup.select('.panel-title')[0].getText()
    genLinks = soup.select('div > p > a')
    deckLink = genLinks[1].get('href')

    # get decklist
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
    
    # score deck completion vs collection
    score = 0
    scorePoss = 1 # general not in decklist

    if general in deckList:
        score += 1

    gOwn = False
    if general in collection:
        gOwn = True

    # include general in card list for easy importing
    if gOwn:
        print('* 1 ' + general)
    else:
        print('  1 ' + general)

    for i in deckList:
        own = False
        if i.startswith('1 '): # if a single (i.e. not a basic land) card in the list
            scorePoss += 1
            if i[2:] in collection:
                score += 1
                own = True
        if own:
            print('* ' + i)
        else:
            print('  ' + i)

    print()
    print('Score: ' + str(score) + ' of a possible ' + str(scorePoss)
          + ' (' + str(round((score / scorePoss) * 100)) + '%)')
    
    return

def calcScore(collection, general, deckList):
    # score deck completion vs collection and return score and scorePoss
    score = 0
    scorePoss = 1 # general not in decklist

    if general in deckList:
        score += 1

    for i in deckList:
        if i.startswith('1 '): # if a single (i.e. not a basic land) card in the list
            scorePoss += 1
            if i[2:] in collection:
                score += 1

    return score, scorePoss

def getCount(count, collection):
    # set up some variables
    general = ''
    deckList = ''
    score = 0
    scorePoss = 1

    # let user know we're working
    print('Retrieving and ranking ' + str(count) + ' potential generals...')

    # call getRandom in a loop and do science to it
    for x in range(0, int(count)):
        lGeneral, lDeckList = getRandom()
        lScore, lScorePoss = calcScore(collection, lGeneral, lDeckList)
        print('Found "' + lGeneral + '", score ' + str(lScore) + '/' + str(lScorePoss) + '(' + str(round((lScore / lScorePoss) * 100)) + '%).')
        if round((lScore / lScorePoss) * 100) > round((score / scorePoss) * 100):
            general = lGeneral
            deckList = lDeckList
            score = lScore
            scorePoss = lScorePoss

    return general, deckList

# --- start program ---
# set up argument parser
parser = argparse.ArgumentParser(description='edhScore.py - Pulls a general from edhrec.com/local decklist and scores vs inventory csv. ONLY ONE ARGUMENT ACCEPTED AT A TIME. If more than one argument is specified, you\'ll have to learn the order they\'re parsed in to get a sensible result.')
parser.add_argument('-c','--count',help='# of possible generals to retrieve and rank. Outputs highest-scoring general and list.',default='empty',required=False)
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
elif (args.count is not 'empty'):
    # handle ranking
    collection = importColl()
    general, deckList = getCount(args.count, collection)
    printInfo(collection, general, deckList)
else:
    # random general
    collection = importColl()
    print('Getting random general...')
    general, deckList = getRandom()
    printInfo(collection, general, deckList)
