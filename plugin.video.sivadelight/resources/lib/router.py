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

HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def routing(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring[1:])) if paramstring else {}
    mode = params.get('mode')
    
    if not mode:
        # Step 1: Main Menu (Based on your Category Screenshot)
        add_directory_item("TamilGun Latest", "https://tamilgun.now/movies.html", "list", True)
        add_directory_item("HD Movies", "https://tamilgun.now/video-category/hd-movies/", "list", True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif mode == 'list':
        # Step 2: Category Page (Based on image_8befa6.jpg)
        scrape_category(params['url'])
    elif mode == 'play':
        # Step 3: Movie Page / Players (Based on image_8becbf.png)
        resolve_and_play(params['url'])

def scrape_category(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Regex is safer here to avoid picking up the 'width=' layout junk
        # It looks for the link and the title inside the video tiles
        matches = re.findall(r'href="(https://tamilgun.now/video/[^"]+)"[^>]*>.*?alt="([^"]+)"', r.text, re.DOTALL)
        
        if not matches:
            # Fallback search if the first one fails
            matches = re.findall(r'href="(https://tamilgun.now/video/[^"]+)".*?title="([^"]+)"', r.text, re.DOTALL)

        for m_url, title in matches:
            # Filter out repeats and layout junk
            if "width=" in title or "TamilGun" in title and len(title) < 10:
                continue
            add_directory_item(title, m_url, "play", False)
            
        if not matches:
            xbmcgui.Dialog().notification("SivaDelight", "No movies found in this category")

    except Exception as e:
        xbmcgui.Dialog().ok("Scraper Error", str(e))
    
    xbmcplugin.endOfDirectory(HANDLE)

def resolve_and_play(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://tamilgun.now/'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Look for the "Player" buttons seen in image_8becbf.png
        # These are usually iframes or direct links to hosts like streamwire
        players = re.findall(r'href="(https?://(?:streamwire|mixdrop|dood|voe|vudeo)\.[a-z0-9/._-]+)"', r.text)
        
        if not players:
            # Look for iframe players if buttons aren't direct links
            players = re.findall(r'iframe.*?src="([^"]+)"', r.text)

        resolved = False
        if resolveurl:
            for p_url in players:
                hmf = resolveurl.HostedMediaFile(url=p_url)
                if hmf:
                    video_url = hmf.resolve()
                    if video_url:
                        listitem = xbmcgui.ListItem(path=video_url)
                        xbmcplugin.setResolvedUrl(HANDLE, True, listitem)
                        resolved = True
                        break
        
        if not resolved:
            xbmcgui.Dialog().ok("SivaDelight", "Could not resolve Player 1 or Player 2")

    except Exception as e:
        xbmcgui.Dialog().ok("Playback Error", str(e))

def add_directory_item(name, url, mode, isFolder, thumb=None):
    list_item = xbmcgui.ListItem(label=name)
    if thumb:
        list_item.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
    if not isFolder:
        list_item.setProperty('IsPlayable', 'true')
    
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{BASE_URL}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=isFolder)
