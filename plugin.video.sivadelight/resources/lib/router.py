import sys
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Setup global variables from sys.argv
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def routing(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring[1:])) if paramstring else {}
    mode = params.get('mode')
    
    if not mode:
        # Initial Menu
        add_directory_item("TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif mode == 'list':
        scrape_movies(params['url'])

def scrape_movies(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # This targets the "Latest Videos" grid items from your screenshot
        # In the current TamilGun layout, these are often in 'div' tags with classes like 'post-column'
        items = soup.find_all('div', class_=lambda x: x and 'post' in x)
        
        found = False
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                title = img_tag.get('alt') or link_tag.get('title')
                movie_url = link_tag.get('href')
                thumb = img_tag.get('src') or img_tag.get('data-src')
                
                if movie_url and title:
                    # Clean up the thumb URL
                    if thumb and thumb.startswith('//'): thumb = 'https:' + thumb
                    
                    add_directory_item(title, movie_url, "play", False, thumb)
                    found = True
        
        if not found:
            xbmcgui.Dialog().notification("SivaDelight", "No movies found. Site layout may have changed.")

    except Exception as e:
        xbmcgui.Dialog().ok("Error", str(e))
    
    xbmcplugin.endOfDirectory(HANDLE)

def add_directory_item(name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{BASE_URL}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=isFolder)
