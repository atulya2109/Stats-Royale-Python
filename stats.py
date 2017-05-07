from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
#from flask import Flask
#from flask import request

#app=Flask(__name__)

#@app.route('/refesh/')
def refresh():
    tag='PL2UV8J'
    obj_list=[]
    url="http://statsroyale.com/profile/"+tag
    req=Request(url,headers={'User-Agent':'Mozilla/5.0(Windows;U;Windows NT 6.1; v2.2) Gecko/20110201'})
    page=urlopen(req).read()
    soup=BeautifulSoup(page,"lxml")
    elems=soup.find_all('div',{'class':'col-sm-4'})
    for elem in elems:
        desc=elem.find('div',class_='description').getText()
        cont=elem.find('div',class_='content').getText()
        if not cont is None or description is None:
            obj={desc:cont}
    print(obj_list)

if __name__ == '__main__':
    refresh()
    # app.debug=True
    # app.run(host='127.0.0.1',port=5000)
