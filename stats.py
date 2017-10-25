from bs4 import BeautifulSoup
from json import loads
from flask import Flask, request
from time import sleep
import requests

app = Flask(__name__)

'''Profile tags for testing '''
# 9890JJJV, PRR2LUGO, 9VUQUGCP, PL2UV8J
# 8QU0PCQ

'''Clan tags for testing'''
# QQPPJRL, 2CQQVQCU, QYLPC9C, G9CL0QJ
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
		link = 'http://statsroyale.com/matches/' + tag
	elif element == 'clan':
		link = 'http://statsroyale.com/clan/' + tag
	response = requests.get(link).text
	soup = BeautifulSoup(response, 'html.parser')
	return soup

# Refresh player battles
@app.route('/refresh/')
def refresh(tag, element):
	tag = getTag(tag)
	if element == 'profile':
		link = 'http://statsroyale.com/profile/' + tag + '/refresh'
	elif element == 'battles':
		link = 'http://statsroyale.com/battles/' + tag + '/refresh'
	elif element == 'clan':
		link = 'http://statsroyale.com/clan/' + tag + '/refresh'
	return requests.get(link)

# Return player's username, level, clan, clan tag.

def getProfileBasic(tag):
	soup = parseURL(tag, element='profile')
	# basic = soup.find('div', {'class':'statistics__userInfo'}
	stats = {}

	level = soup.find('span', {'class':'profileHeader__userLevel'}).get_text()
	stats[u'level'] = int(level)

	username = soup.find('div', {'class':'ui__headerMedium profileHeader__name'}).get_text()
	username = username.strip('\n')[:-3].strip()
	stats[u'username'] = username

	# clan = soup.find('profileHeader__userClan').get_text().replace(level, '').replace(username, '').strip()
	clan = soup.find('a',{'class':'profileHeader__userClan'})
	clan_name = clan.get_text().strip()

	if clan == 'No Clan':
		stats[u'clan'] = None
		stats[u'clan tag'] = '#'
	else:
		stats[u'clan'] = clan_name
		clan_tag = '#' + clan['href'][6:].strip()
		stats[u'clan tag'] = clan_tag

	return stats


# Return highest_trophies, donations, etc.
@app.route('/profile?tag')
def getProfile(tag, refresh=False):
	if refresh:
		refresh(tag, element='profile')
		sleep(20.1)
	stats = getProfileBasic(tag)
	soup = parseURL(tag, element='profile')

	stats[u'profile'] = {}
	profile = soup.find('div', {'class':'statistics__metrics'})

	for div in profile.find_all('div', {'class':'statistics__metric'}):
		result = (div.find_all('div')[0].get_text().strip('\n')).strip()
		try:
			result = int(result)
		except ValueError:
			pass
		item = div.find_all('div')[1].get_text().strip('_').lower()
		stats[u'profile'][item] = result
	return stats

# Get battles stats for both winner and loser
def getBattleSide(area, side):
	battles = {}
	side = area.find('div', {'class':'replay__player replay__' + side + 'Player'})

	username = side.find('div', {'class':'replay__userName'}).get_text()
	battles[u'username'] = username.strip()

	clan = side.find('div', {'class':'replay__clanName ui__mediumText'}).get_text()
	clan = clan.strip()

	if clan == 'No Clan':
		battles[u'clan'] = None
	else:
		battles[u'clan'] = clan

	try:
		trophies = side.find('div', {'class':'replay__trophies'}).get_text().strip()
		battles[u'trophies'] = trophies

	except Exception as e:
		battles[u'trophies'] = 'Not Available'


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

	environment = soup.find_all('div', {'class':'replay__container'})
	battles = []

	for area in environment:
		battle = {}
		battle[u'event'] = area['data-type']
		
		date = area.find('div', {'class':'replay__date ui__smallText'}).get_text().strip()
		battle[u'date'] = date

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
	clan[u'name'] = title.strip()

	description = soup.find('div', {'class':'ui__mediumText'}).get_text()
	clan[u'description'] = description.strip()

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

# Returns a list with each chest as a dictionary which contains chest name an counter
def getChestCycle(tag, refresh=False):
	if refresh:
		refresh(tag, element='profile')
		sleep(20.1)

	chest_cycle={}
	chest_list=[]
	soup = parseURL(tag, element='profile')
	chests_queue = soup.find('div', {'class':'chests__queue'})
	chests = chests_queue.find_all('div')

	for chest in chests:
		if 'chests__disabled' in chest['class'][-1]:
			continue # Disabled chests are those chest that player has already got.

		elif 'chests__next' in chest['class'][-1]:
			chest_list.append({'next_chest':chest['class'][0][8:]}) # class=chests__silver chests__next
			continue

		elif 'chests__' in chest['class'][0]:
			chest_name = chest['class'][0][8:]
			counter=chest.find('span', {'class':'chests__counter'}).get_text()
			chest_list.append({'chest':chest_name, 'counter':counter})

	return chest_list

 # Work In Progress
def getClanMembers(tag, refresh=False):
	if refresh:
		refresh(tag, element='profile')
		sleep(20.1)

	soup = parseURL(tag, element='clan')
	members=[]
	rowContainers = soup.find_all('div', {'class':'clan__rowContainer'})

	for rowContainer in rowContainers:
		member = {}
		info = rowContainer.find_all('div',{'class':'clan__row'})
		member[u'rank'] = int(info[0].get_text().strip().strip('#'))
		username = rowContainer.find('a', {'class':'ui__blueLink'}).get_text().split(' ')
		member[u'username'] = ''.join(username)
		member[u'tag'] = rowContainer.find('a', {'class':'ui__blueLink'})['href'][9:]
		member[u'level'] = rowContainer.find('span', {'class':'clan__playerLevel'}).get_text()
		member[u'trophies'] = int(rowContainer.find('div', {'class':'clan__cup'}).get_text())
		member[u'crowns'] = int(rowContainer.find_all('div', {'class':"clan__row"})[5].get_text())
		member[u'donations'] = rowContainer.find_all('div', {'class':"clan__row"})[6].get_text().strip()
		member[u'role'] = rowContainer.find_all('div', {'class':"clan__row"})[7].get_text().strip()
		members.append(member)

	return members

print(getBattles("PL2UV8J"))

'''Methods That Are Working...'''
# getChestCycle("PL2UV8J")
# getProfileBasic("PL2UV8J")
# getClanBasic("QQPPJRL")
'''Methods Throwing Error...''' # If You Fixed Anyone Of These Please Mention Your Name

'''Fixed !!!'''
# getProfileBasic() by Atulya2109
# getBattleSide() by Atulya2109
# getBattles() by Atulya2109
# getClanMembers() by Gogit2194
'''Uncomment to run in browser'''
# if __name__ == '__main__':
#     app.run(host = '127.0.0.1', port = 5000)
