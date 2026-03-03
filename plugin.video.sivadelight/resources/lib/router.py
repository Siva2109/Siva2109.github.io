import sys
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Standard Kodi ResolveURL import pattern
try:
    import resolveurl
except ImportError:
    resolveurl = None

def routing(paramstring, handle):
    # This handles the empty params when you first open the addon
    params = dict(urllib.parse.parse_qsl(paramstring[1:])) if paramstring else {}
    mode = params.get('mode')
    
    if not mode:
        # MAIN MENU - This must always work
        add_directory_item(handle, "TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        add_directory_item(handle, "TamilBulb Movies", "https://tamilbulb.cc/", "list", True)
        xbmcplugin.endOfDirectory(handle)
    
    elif mode == 'list':
        scrape_movies(params['url'], handle)
        
    elif mode == 'play':
        play_movie(params['url'], handle)

def scrape_movies(url, handle):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Look for movie links
        found = False
        for item in soup.find_all('a'):
            img = item.find('img')
            if img and item.get('href') and ('/video/' in item.get('href') or 'tamilbulb' in item.get('href')):
                title = img.get('alt') or item.get('title') or "Movie"
                movie_link = item.get('href')
                thumb = img.get('src')
                
                if movie_link.startswith('/'):
                    movie_link = 'https://tamilgun.now' + movie_link
                
                add_directory_item(handle, title, movie_link, "play", False, thumb)
                found = True
        
        if not found:
            xbmcgui.Dialog().notification("SivaDelight", "No movies found on page")
            
    except Exception as e:
        xbmcgui.Dialog().ok("Scraper Error", str(e))
    
    xbmcplugin.endOfDirectory(handle)

def play_movie(url, handle):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "ResolveURL missing. Install via Gujal Repo.")
        return

    try:
        # Use ResolveURL to find the playable video stream
        hmf = resolveurl.HostedMediaFile(url=url)
        if hmf:
            video_url = hmf.resolve()
            if video_url:
                listitem = xbmcgui.ListItem(path=video_url)
                xbmcplugin.setResolvedUrl(handle, True, listitem)
                return
        
        xbmcgui.Dialog().notification("SivaDelight", "Link not supported by ResolveURL")
    except Exception as e:
        xbmcgui.Dialog().ok("Playback Error", str(e))

def add_directory_item(handle, name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    
    # Critical: Set IsPlayable for movies, not folders
    if not isFolder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': name})
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=isFolder)
