from bs4 import BeautifulSoup
import time
import requests


'''Profile tags for testing '''
# 9890JJJV, PRR2LUGO, 9VUQUGCP, PL2UV8J
# 8QU0PCQ

'''Clan tags for testing'''
# 2CQQVQCU, QYLPC9C, G9CL0QJ
# statsroyale.com/clan/2CQQVQCU


# Return player tag taking input as URL or player tag itself
def get_tag(tag):
    if not tag.find('/') == -1:
        tag = tag[::-1]
        pos = tag.find('/')
        tag = tag[:pos]
        tag = tag[::-1]
    return tag


# Return parsed profile page using BS4
def parse_url(tag, element):
    tag = get_tag(tag)
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
    tag = get_tag(tag)
    if element == 'profile':
        link = 'http://statsroyale.com/profile/' + tag + '/refresh'
    elif element == 'battles':
        link = 'http://statsroyale.com/battles/' + tag + '/refresh'
    elif element == 'clan':
        link = 'http://statsroyale.com/clan/' + tag + '/refresh'
    return requests.get(link)


# Return player's username and level
def profile_basic(tag):
    soup = parse_url(tag, element='profile')
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
def profile(tag, refresh=False):
    if refresh:
        refresh(tag, element='profile')
        time.sleep(20.1)
    stats = profile_basic(tag)
    soup = parse_url(tag, element='profile')

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
def battle_side(area, side):
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
def battles(tag, event='all', refresh=False):
    tag = get_tag(tag)
    if refresh:
        refresh(tag, element='battles')
        time.sleep(8.1)

    soup = parse_url(tag, element='battles')

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

        battle[u'left'] = battle_side(area, side='left')
        battle[u'right'] = battle_side(area, side='right')

        battles.append(battle)

    return battles


def clan_basic(tag):
    soup = parse_url(tag, element='clan')
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
def clan(tag, refresh=False):
    tag = get_tag(tag)
    soup = parse_url(tag, element='clan')
    if refresh:
        refresh(tag, element='clan')
    clan = clan_basic(tag)
    return clan


# Returns a list with each chest as a dictionary which contains chest name an counter.
def chest_cycle(tag, refresh=False):
    if refresh:
        refresh(tag, element='profile')
        time.sleep(20.1)
    chest_cycle = {}
    chest_list = []
    soup = parse_url(tag, element='profile')
    chests_queue = soup.find('div', {'class':'chests__queue'})
    chests = chests_queue.find_all('div')
    for chest in chests:
        if 'chests__disabled' in chest['class'][-1]:
            continue # Disabled chests are those chest that player has already got.
        elif 'chests__next' in chest['class'][-1]:
            chest_list.append({'next_chest':chest['class'][0][8:]}) # class=chests__silver chests__next
            continue
        elif 'chests__' in chest['class'][0]:
            print (chest['class'][0])
            chest_name = chest['class'][0][8:]
            counter = chest.find('span', {'class':'chests__counter'}).get_text()
            chest_list.append({'chest':chest_name, 'counter':counter})
    return chest_list


stats = profile(tag='9890JJJV', refresh=False)
print(stats)

battles = battles(tag='9890JJJV', event='all', refresh=False)
#for x in battles:
    #print(x)

print(battles[0])
#print(battles[0]['result']['wins'])
#print(battles[0]['left']['troops']['skeleton_horde'])

clan = clan(tag='2CQQVQCU', refresh=False)
print(clan)

print(chest_cycle(tag='PL2UV8j', refresh=False))
