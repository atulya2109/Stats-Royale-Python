from bs4 import BeautifulSoup
from json import loads
from time import sleep
import requests

''' Tags for testing '''
# 9890JJJV
# PRR2LUGO
# 9VUQUGCP

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
	basic = soup.find('div', {'class':'statistics__name'})
	stats = {}
	stats[u'level'] = basic.find('span').get_text()
	stats[u'username'] = max(basic.find('div').get_text().replace('\n', '').split(' '))
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
	stats[u'profile'] = {}
	soup = parseURL(tag)
	profile = soup.find('div', {'class':'statistics__metrics'})
	for div in profile.find_all('div', {'class':'statistics__metric'}):
		result = max(div.find_all('div')[0].get_text().replace('\n', '').split(' '))
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
	if refresh:
		refreshBattles(tag)
		sleep(8.1)
	soup = parseURL(soup)
	return

stats = getProfile(tag='9890JJJV', refresh=False)
print(stats)

#battles = getBattles(tag='9890JJJV', event='all', refresh=False)
#print(battles)
