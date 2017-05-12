from bs4 import BeautifulSoup
from json import loads
from time import sleep
import requests

'''Profile tags for testing '''
# 9890JJJV, PRR2LUGO, 9VUQUGCP, PL2UV8J
# 8QU0PCQ

'''Clan tags for testing'''
# 2CQQVQCU, QYLPC9C, G9CL0QJ
# statsroyale.com/clan/2CQQVQCU

# Return player tag taking input as URL or player tag itself
def getTag(tag):
	if not tag.find('/') == -1:
		tag = tag[::-1]
		pos = tag.find('/')
		tag = tag[:pos]
		tag = tag[::-1]
	return tag

# Return parsed profile page using BS4
def parseURL(tag, element):
	tag = getTag(tag)
	if element == 'profile':
		link = 'http://statsroyale.com/profile/' + tag
	elif element == 'battles':
		link = 'http://statsroyale.com/profile/' + tag
	elif element == 'clan':
		link = 'http://statsroyale.com/clan/' + tag
	response = requests.get(link).text
	soup = BeautifulSoup(response, 'html.parser')
	return soup

# Refresh player battles
def refresh(tag, element):
	tag = getTag(tag)
	if element == 'profile':
		link = 'http://statsroyale.com/profile/' + tag + '/refresh'
	elif element == 'battles':
		link = 'http://statsroyale.com/battles/' + tag + '/refresh'
	elif element == 'clan':
		link = 'http://statsroyale.com/clan/' + tag + '/refresh'
	return requests.get(link)

# Return player's username and level
def getProfileBasic(tag):
	soup = parseURL(tag, element='profile')
	basic = soup.find('div', {'class':'statistics__userInfo'})
	stats = {}

	level = basic.find('span', {'class':'statistics__userLevel'}).get_text()
	stats[u'level'] = int(level)

	username = basic.find('div', {'class':'ui__headerMedium statistics__userName'}).get_text()
	username = username.replace('\n', '')[:-3].lstrip().rstrip()
	stats[u'username'] = username

	clan = basic.get_text().replace(level, '').replace(username, '').lstrip().rstrip()
	if clan == 'No Clan':
		stats[u'clan'] = None
	else:
		stats[u'clan'] = clan

	return stats


# Return highest_trophies, donations, etc
def getProfile(tag, refresh=False):
	if refresh:
		refresh(tag, element='profile')
		sleep(20.1)
	stats = getProfileBasic(tag)
	soup = parseURL(tag, element='profile')

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

# Get battles stats for both winner and loser
def getBattleSide(area, side):
	battles = {}
	side = area.find('div', {'class':'replay__player replay__' + side + 'Player'})

	username = side.find('div', {'class':'replay__userName'}).get_text()
	battles[u'username'] = username.lstrip().rstrip()

	clan = side.find('div', {'class':'replay__clanName ui__mediumText'}).get_text()
	clan = clan.lstrip().rstrip()

	if clan == 'No Clan':
		battles[u'clan'] = None
	else:
		battles[u'clan'] = clan

	trophies = side.find('div', {'class':'replay__trophies'}).get_text()
	battles[u'trophies'] = int(trophies.lstrip().rstrip())

	battles[u'troops'] = {}

	troops = side.find_all('div', {'class':'replay__card'})
	for troop in troops:
		troop_name = troop.find('img')['src'].replace('/images/cards/full/', '')
		troop_name = troop_name[:-4]

		level = troop.find('span').get_text()
		level = int(level.replace('Lvl', ''))
		battles[u'troops'][troop_name] = level

	return battles

# Get battle summary
def getBattles(tag, event='all', refresh=False):
	tag = getTag(tag)
	if refresh:
		refresh(tag, element='battles')
		sleep(8.1)

	soup = parseURL(tag, element='battles')

	environment = soup.find_all('div', {'class':'replay'})
	battles = []

	for area in environment:
		battle = {}
		battle[u'event'] = area['data-type']

		outcome = area.find('div', {'class':'replay__win ui__headerExtraSmall'})

		if outcome == None:
			battle[u'outcome'] = 'defeat'
		else:
			battle[u'outcome'] = 'victory'

		result = area.find('div', {'class':'replay__recordText ui__headerExtraSmall'}).get_text()
		battle[u'result'] = {}

		wins = int(result.split(' ')[0])
		losses = int(result.split(' ')[-1])
		battle[u'result'][u'wins'], battle[u'result'][u'losses'] = wins, losses

		battle[u'left'] = getBattleSide(area, side='left')
		battle[u'right'] = getBattleSide(area, side='right')

		battles.append(battle)

	return battles

def getClanBasic(tag):
	soup = parseURL(tag, element='clan')
	clan = {}

	title = soup.find('div', {'class':'ui__headerMedium clan__clanName'}).get_text()
	clan[u'name'] = title.lstrip().rstrip()

	description = soup.find('div', {'class':'ui__mediumText'}).get_text()
	clan[u'description'] = description.lstrip().rstrip()

	clan_stats = soup.find_all('div', {'class':'clan__metricContent'})

	for div in clan_stats:
		item = div.find('div', {'class':'ui__mediumText'}).get_text()
		item = item.replace('/', '_').replace(' ', '_').lower()
		result = div.find('div', {'class':'ui__headerMedium'}).get_text()
		result = int(result)
		clan[item] = result

	return clan

# Work in progress
def getClan(tag, refresh=False):
	tag = getTag(tag)
	soup = parseURL(tag, element='clan')
	if refresh:
		refresh(tag, element='clan')
	clan = getClanBasic(tag)
	return clan

# Work in progress
def getChestCycle(tag, refresh=False):
	if refresh:
		refresh(tag, element='profile')
		sleep(20.1)
		chest_cycle = {}
	soup = parseURL(tag, element='profile')
	chests_queue = soup.find('div', {'class':'chests_queue'})
	chests = chests_queue.find_all('div')
	for chest in chests:
		if 'disabled' in chest['class']:
			continue
		if 'next' in chest['class']:
			pos = chest['class'].rfind('_')
			chest_cycle['next_chest'] = chest['class'][9:pos-2]
			continue

#stats = getProfile(tag='9890JJJV', refresh=False)
#print(stats)

#battles = getBattles(tag='9890JJJV', event='all', refresh=False)
#for x in battles:
#	print(x)

#print(battles[0])
#print(battles[0]['result']['wins'])
#print(battles[0]['left']['troops']['skeleton_horde'])

clan = getClan(tag='2CQQVQCU', refresh=False)
print(clan)
