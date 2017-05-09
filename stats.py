from bs4 import BeautifulSoup
import requests

def statsRoyale(tag):
	if not tag.find('/') == -1:
		tag = tag[::-1]
		pos = tag.find('/')
		tag = tag[:pos]
		tag = tag[::-1]

	link = 'http://statsroyale.com/profile/' + tag
	response = (requests.get(link)).text
	soup = BeautifulSoup(response, 'html.parser')

	description = soup.find_all('div', {'class':'description'})
	content = soup.find_all('div', {'class':'content'})

	stats = {}

	for i in range(len(description)):
		description_text = ((description[i].get_text()).replace(' ', '_')).lower()
		content_text = content[i].get_text()
		stats[description_text] = content_text

	if stats['clan'] == 'No Clan':
		stats['clan'] = None

	return stats

stats = statsRoyale(tag='9890JJJV')
print stats
