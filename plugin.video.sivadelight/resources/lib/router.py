import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

try:
    import resolveurl
except ImportError:
    resolveurl = None

def routing(paramstring, handle): # Matches Deccan Delight's routing(argv[2])
    params = dict(urllib.parse.parse_qsl(paramstring[1:]))
    mode = params.get('mode')
    
    if not mode:
        # Main Menu
        add_directory_item(handle, "TamilGun Movies", "https://tamilgun.now/movies.html", "list", True)
        xbmcplugin.endOfDirectory(handle)
    
    elif mode == 'list':
        scrape_movies(params['url'], handle)
        
    elif mode == 'play':
        play_movie(params['url'], handle)

def scrape_movies(url, handle):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Look for all links that have movie posters
        for item in soup.find_all('a'):
            img = item.find('img')
            if img and item.get('href') and '/video/' in item.get('href'):
                title = img.get('alt') or "Movie"
                movie_link = item.get('href')
                thumb = img.get('src')
                
                # We set isFolder=False so it tries to PLAY when clicked
                add_directory_item(handle, title, movie_link, "play", False, thumb)
    except:
        pass
    xbmcplugin.endOfDirectory(handle)

def play_movie(url, handle):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "Please install ResolveURL dependency.")
        return

    # This is the "Magic" from Deccan Delight: resolving the link
    hmf = resolveurl.HostedMediaFile(url=url)
    if hmf:
        video_url = hmf.resolve()
        listitem = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(handle, True, listitem)
    else:
        xbmcgui.Dialog().notification("SivaDelight", "Could not find a playable stream.")

def add_directory_item(handle, name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        list_item.setArt({'thumb': thumb, 'poster': thumb})
    list_item.setProperty('IsPlayable', 'true') if not isFolder else None
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=isFolder)
