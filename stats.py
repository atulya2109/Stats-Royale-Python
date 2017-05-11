from bs4 import BeautifulSoup
from json import loads
from time import sleep
import requests

'''Profile tags for testing '''
# 9890JJJV, PRR2LUGO, 9VUQUGCP, PL2UV8J
# 8QU0PCQ

'''Clan tags for testing'''
# 2CQQVQCU, QYLPC9C, G9CL0QJ

# Return player tag taking input as URL or player tag itself
def getTag(tag):
	if not tag.find('/') == -1:
		tag = tag[::-1]
		pos = tag.find('/')
		tag = tag[:pos]
		tag = tag[::-1]
	return tag

# Return parsed profile page using BS4
def parseURL(tag):
	tag = getTag(tag)
	link = 'http://statsroyale.com/profile/' + tag
	response = requests.get(link).text
	soup = BeautifulSoup(response, 'html.parser')
	return soup

# Return player's username and level
def getBasic(tag):
	soup = parseURL(tag)
	basic = soup.find('div', {'class':'statistics__userInfo'})
	stats = {}

	level = basic.find('span', {'class':'statistics__userLevel'}).get_text()
	stats[u'level'] = level

	username = basic.find('div', {'class':'ui__headerMedium statistics__userName'}).get_text()
	username = username.replace('\n', '')[:-3].lstrip().rstrip()
	stats[u'username'] = username

	clan = basic.get_text().replace(level, '').replace(username, '').lstrip().rstrip()
	if clan == 'No Clan':
		stats[u'clan'] = None
	else:
		stats[u'clan'] = clan

	return stats

# Refresh player profile
def refreshProfile(tag):
	tag = getTag(tag)
	link = 'http://statsroyale.com/profile/' + tag + '/refresh'
	return requests.get(link)

# Return highest_trophies, donations, etc
def getProfile(tag, refresh=False):
	if refresh:
		refreshProfile(tag)
		sleep(20.1)
	stats = getBasic(tag)
	soup = parseURL(tag)

	stats[u'profile'] = {}
	profile = soup.find('div', {'class':'statistics__metrics'})

	for div in profile.find_all('div', {'class':'statistics__metric'}):
		result = (div.find_all('div')[0].get_text().replace('\n', '')).lstrip().rstrip()
		try:
			result = int(result)
		except ValueError:
			pass
		item = div.find_all('div')[1].get_text().replace(' ', '_').lower()
		stats[u'profile'][item] = result
	return stats

# Refresh player battles
def refreshBattles(tag):
	tag = getTag(tag)
	link = 'http://statsroyale.com/battles/' + tag + '/refresh'
	return requests.get(link)

# Work in progress
def getBattles(tag, event='all', refresh=False):
	tag = getTag(tag)
	if refresh:
		refreshBattles(tag)
		sleep(8.1)
	soup = parseURL(tag)
	# iterate over summary
	summary = soup.find_all('div', {'class':'replay'})[0]
	#print match
	battles = {}

	battles[u'event'] = summary['data-type']

	outcome = summary.find('div', {'class':'replay__win ui__headerExtraSmall'})
	battles[u'outcome'] = outcome.get_text().lower()

	result = summary.find('div', {'class':'replay__recordText ui__headerExtraSmall'}).get_text()
	battles[u'result'] = {}

	wins = result.split(' ')[0]
	losses = result.split(' ')[-1]
	battles[u'result'][u'wins'],  battles[u'result'][u'losses'] = wins, losses

	battles[u'left'] = {}
	left = summary.find('div', {'class':'replay__player replay__leftPlayer'})

	username = left.find('div', {'class':'replay__userName'}).get_text()
	battles[u'left'][u'username'] = username.lstrip().rstrip()

	clan = left.find('div', {'class':'replay__clanName ui__mediumText'}).get_text()
	battles[u'left'][u'clan'] = clan.lstrip().rstrip()

	trophies = left.find('div', {'class':'replay__trophies'}).get_text()
	battles[u'left'][u'trophies'] = trophies.lstrip().rstrip()

	battles[u'left'][u'troops'] = {}

	troops = left.find_all('div', {'class':'replay__card'})
	for troop in troops:
		troop_name = troop.find('img')['src'].replace('/images/cards/full/', '')
		troop_name = troop_name[:-4]

		level = troop.find('span').get_text()
		level = int(level.replace('Lvl', ''))
		battles[u'left'][u'troops'][troop_name] = level

	return battles

# Work in progress
def getChestCycle(tag, refresh=False):
	if refresh:
		refreshProfile(tag)
		sleep(20.1)
		chest_cycle = {}
	soup = parseURL(tag)
	chests_queue = soup.find('div', {'class':'chests_queue'})
	chests = chests_queue.find_all('div')
	for chest in chests:
		if 'disabled' in chest['class']:
			continue
		if 'next' in chest['class']:
			pos = chest['class'].rfind('_')
			chest_cycle['next_chest'] = chest['class'][9:pos-2]
			continue

stats = getProfile(tag='9890JJJV', refresh=False)
print(stats)

battles = getBattles(tag='9890JJJV', event='all', refresh=False)
print(battles)
