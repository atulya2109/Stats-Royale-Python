from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
from flask import Flask
import json
from flask import request

app=Flask(__name__)

@app.route('/refresh/user')
def refresh():
    tag=request.args.get("tag")
    obj_list=[]
    url="http://www.statsroyale.com/profile/"+tag
    req=Request(url,headers={'User-Agent':'Mozilla/5.0(Windows;U;Windows NT 6.1; v2.2) Gecko/20110201'})
    page=urlopen(req).read()
    soup=BeautifulSoup(page,"lxml")
    elems=soup.find_all('div',{'class':'col-sm-4' })
    player_info=soup.find('div', class_='playerlevel')
    level=player_info.find('span', class_='supercell').getText()
    player_page=soup.find("div",class_='panel-title')
    player=player_page.find_all('span',class_='supercell')[1]
    player_obj={'Name':player.getText(),'Level':level}
    obj_list.append(player_obj)
    for elem in elems:
        #print (elem)
        desc=elem.find('div',class_='description')
        cont=elem.find('div',class_='content')
        if cont is None:
            continue
        if desc is None:
            continue
        get_desc=elem.find('div',class_='description').getText()
        get_cont=elem.find('div',class_='content').getText()
        obj={get_desc:get_cont}
        obj_list.append(obj)
    usr_obj={'Player Details':obj_list}
    return json.dumps(usr_obj)

# def runScript(s):


if __name__ == '__main__':
    app.debug=True
    app.run(host='127.0.0.1',port=5000)
