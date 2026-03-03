import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

def routing(params, handle):
    mode = params.get('mode')
    
    if not mode:
        # Main Menu
        add_directory_item(handle, "TamilGun Movies", "https://tamilgun.now/", "list")
        add_directory_item(handle, "TamilBulb Movies", "https://tamilbulb.cc/", "list")
        xbmcplugin.endOfDirectory(handle)
    
    elif mode == 'list':
        scrape_movies(params['url'], handle)

def scrape_movies(url, handle):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # IMPROVED SCRAPER: Looking for more common Tamil site tags
        # This is likely why your folders were empty before!
        items = soup.find_all(['article', 'div'], class_=['video', 'v-item', 'post', 'ml-item'])
        
        for item in items:
            link = item.find('a')['href']
            title = item.find('img').get('alt') or "Movie"
            img = item.find('img').get('src')
            
            list_item = xbmcgui.ListItem(label=title)
            list_item.setArt({'thumb': img, 'poster': img})
            list_item.setInfo('video', {'title': title})
            
            xbmcplugin.addDirectoryItem(handle=handle, url=link, listitem=list_item, isFolder=True)
            
    except Exception as e:
        xbmcgui.Dialog().notification("SivaDelight", "Scrape Failed")
    
    xbmcplugin.endOfDirectory(handle)

def add_directory_item(handle, name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=True)
