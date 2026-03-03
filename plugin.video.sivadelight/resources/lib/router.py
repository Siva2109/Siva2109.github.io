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
        # Main Menu
        add_directory_item(handle, "TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        add_directory_item(handle, "TamilBulb Movies", "https://tamilbulb.cc/", "list", True)
        xbmcplugin.endOfDirectory(handle)
    
    elif mode == 'list':
        scrape_movies(params['url'], handle)
        
    elif mode == 'play':
        play_movie(params['url'], handle)

def scrape_movies(url, handle):
    # Using a Session to handle cookies like Deccan Delight does
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://tamilgun.now/'
    }
    
    try:
        r = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # This is the "Oct 2025 Fix": TamilGun now wraps movies in 'article' or 'div' with specific classes
        items = soup.find_all(['article', 'div'], class_=['post', 'v-item', 'ml-item', 'video'])
        
        found = False
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                title = img_tag.get('alt') or link_tag.get('title') or "Movie"
                movie_url = link_tag.get('href')
                thumb = img_tag.get('src') or img_tag.get('data-src')

                if movie_url and movie_url.startswith('http'):
                    # Fix image links
                    if thumb and thumb.startswith('//'): thumb = 'https:' + thumb
                    
                    # Add as a playable item
                    add_directory_item(handle, title, movie_url, "play", False, thumb)
                    found = True
        
        if not found:
            # Fallback: Just look for any link containing /video/
            for a in soup.find_all('a', href=True):
                if '/video/' in a['href']:
                    img = a.find('img')
                    if img:
                        add_directory_item(handle, img.get('alt', 'Movie'), a['href'], "play", False, img.get('src'))
                        found = True

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", "Site connection failed")
    
    xbmcplugin.endOfDirectory(handle)

def play_movie(url, handle):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "ResolveURL Missing")
        return

    hmf = resolveurl.HostedMediaFile(url=url)
    if hmf:
        video_url = hmf.resolve()
        if video_url:
            listitem = xbmcgui.ListItem(path=video_url)
            xbmcplugin.setResolvedUrl(handle, True, listitem)
            return
    
    xbmcgui.Dialog().notification("SivaDelight", "ResolveURL could not find a link")

def add_directory_item(handle, name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    
    if not isFolder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': name})
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=isFolder)
