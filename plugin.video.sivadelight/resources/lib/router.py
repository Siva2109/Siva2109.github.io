import sys
import xbmcgui
import xbmcplugin
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

try:
    import resolveurl
except ImportError:
    resolveurl = None

# Get the handle and plugin URL globally like Gujal does
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def routing(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring[1:])) if paramstring else {}
    mode = params.get('mode')
    
    if not mode:
        add_directory_item("TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        add_directory_item("TamilBulb", "https://tamilbulb.cc/", "list", True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif mode == 'list':
        scrape_movies(params['url'])
    elif mode == 'play':
        play_movie(params['url'])

def scrape_movies(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://tamilgun.now/'}
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        html = r.text
        
        # 1. Try BeautifulSoup first (Standard)
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(['div', 'article'], class_=['post', 'v-item', 'ml-item'])
        
        found = False
        for item in items:
            link = item.find('a')
            img = item.find('img')
            if link and img:
                title = img.get('alt') or link.get('title')
                m_url = link.get('href')
                thumb = img.get('data-src') or img.get('src')
                if m_url and '/video/' in m_url:
                    add_directory_item(title, m_url, "play", False, thumb)
                    found = True

        # 2. REGEX FALLBACK (The Gujal Secret)
        # If BeautifulSoup finds nothing, we search the raw text for video links
        if not found:
            # Look for patterns like: href="link" ... src="image"
            matches = re.findall(r'href="(https://tamilgun.now/video/[^"]+)"[^>]*>.*?src="([^"]+)"', html, re.DOTALL)
            for m_url, thumb in matches:
                title = m_url.split('/')[-1].replace('-', ' ').title()
                add_directory_item(title, m_url, "play", False, thumb)
                found = True

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", str(e))
    
    xbmcplugin.endOfDirectory(HANDLE)

def play_movie(url):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "ResolveURL Missing")
        return
    hmf = resolveurl.HostedMediaFile(url=url)
    if hmf:
        video_url = hmf.resolve()
        if video_url:
            listitem = xbmcgui.ListItem(path=video_url)
            xbmcplugin.setResolvedUrl(HANDLE, True, listitem)
            return
    xbmcgui.Dialog().notification("SivaDelight", "Stream not found")

def add_directory_item(name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        if thumb.startswith('//'): thumb = 'https:' + thumb
        list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    
    if not isFolder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': name})
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{BASE_URL}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=isFolder)
