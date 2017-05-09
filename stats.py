from bs4 import BeautifulSoup
import requests

def statsRoyale(tag):
	link = 'http://statsroyale.com/profile/' + tag
	responsef = (requests.get(link)).text
	soup = BeautifulSoup(response, 'html.parser')
	stats = {}

	content = soup.find_all('div', {'class':'content'})
	stats['clan'] = content[0].get_text()
	if stats['clan'] == 'No Clan':
		stats['clan'] = None
	stats['highest_trophies'] = content[1].get_text()
	stats['last_known_trophies'] = content[2].get_text()
	stats['challenge_cards_won'] = content[3].get_text()
	stats['tournament_cards_won'] = content[4].get_text()
	stats['total_donations'] = content[5].get_text()
	stats['best_session_rank'] = content[6].get_text()
	stats['previuos_session_rank'] = content[7].get_text()
	stats['legendary_trophies'] = content[8].get_text()
	stats['wins'] = content[9].get_text()
	stats['losses'] = content[10].get_text()
	stats['3_crown_wins'] = content[11].get_text()
	return stats

stats = statsRoyale(tag='9890JJJV')
print stats
