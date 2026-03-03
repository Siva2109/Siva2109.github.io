import sys
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

try:
    import resolveurl
except ImportError:
    resolveurl = None

def routing(paramstring, handle):
    params = dict(urllib.parse.parse_qsl(paramstring[1:])) if paramstring else {}
    mode = params.get('mode')
    
    if not mode:
        # POINT TO THE NEW 2025 GALLERY LINK
        add_directory_item(handle, "TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        add_directory_item(handle, "TamilBulb Movies", "https://tamilbulb.cc/", "list", True)
        xbmcplugin.endOfDirectory(handle)
    
    elif mode == 'list':
        scrape_movies(params['url'], handle)
    elif mode == 'play':
        play_movie(params['url'], handle)

def scrape_movies(url, handle):
    session = requests.Session()
    # The 'Referer' and 'Origin' headers are now required after the Oct update
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://tamilgun.now/',
        'Origin': 'https://tamilgun.now'
    }
    
    try:
        r = session.get(url, headers=headers, timeout=15, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # New search pattern for the Oct 2025 site layout
        items = soup.find_all(['div', 'article'], class_=['post', 'v-item', 'ml-item'])
        
        found = False
        for item in items:
            link = item.find('a')
            img = item.find('img')
            
            if link and img:
                title = img.get('alt') or link.get('title')
                movie_url = link.get('href')
                poster = img.get('data-src') or img.get('src')
                
                if movie_url and '/video/' in movie_url:
                    if poster and poster.startswith('//'): poster = 'https:' + poster
                    add_directory_item(handle, title, movie_url, "play", False, poster)
                    found = True
        
        if not found:
            xbmcgui.Dialog().notification("SivaDelight", "Site layout changed. Trying backup search.")

    except Exception as e:
        xbmcgui.Dialog().ok("Connection Error", str(e))
    
    xbmcplugin.endOfDirectory(handle)

def play_movie(url, handle):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "ResolveURL Missing")
        return
    # Deccan Delight uses HostedMediaFile for these specific sites
    hmf = resolveurl.HostedMediaFile(url=url)
    if hmf:
        video_url = hmf.resolve()
        if video_url:
            listitem = xbmcgui.ListItem(path=video_url)
            xbmcplugin.setResolvedUrl(handle, True, listitem)
            return
    xbmcgui.Dialog().notification("SivaDelight", "No playable stream found")

def add_directory_item(handle, name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb: list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    if not isFolder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': name})
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=isFolder)
