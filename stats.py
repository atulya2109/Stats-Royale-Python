from bs4 import BeautifulSoup
from json import loads
from time import sleep
import requests

#9890JJJV
#PRR2LUGO
#9VUQUGCP

def refreshProfile(tag):
	link = 'http://statsroyale.com/profile/' + tag + '/refresh'
	requests.get(link)

def statsRoyale(tag, refresh=False):
	if not tag.find('/') == -1:
		tag = tag[::-1]
		pos = tag.find('/')
		tag = tag[:pos]
		tag = tag[::-1]

	link = 'http://statsroyale.com/profile/' + tag
	response = requests.get(link).text
	soup = BeautifulSoup(response, 'html.parser')

	if refresh:
		refreshProfile(tag)
		sleep(20.1)

	stats = {}

	try:
		basic = soup.find('div', {'class':'statistics__name'})
		#print(basic)

		stats[u'level'] = basic.find('span').get_text()
		stats[u'username'] = max(basic.find('div').get_text().replace('\n', '').split(' '))

		stats[u'profile'] = {}

		profile = soup.find('div', {'class':'statistics__metrics'})
		for div in profile.find_all('div', {'class':'statistics__metric'}):
			result = max(div.find_all('div')[0].get_text().replace('\n', '').split(' '))
			item = div.find_all('div')[1].get_text().replace(' ', '_').lower()
			stats[u'profile'][item] = result
	except:
		pass

	return stats

#stats = statsRoyale(tag='9890JJJV', refresh=True)
stats = statsRoyale(tag='9890JJJV')

print(stats)
