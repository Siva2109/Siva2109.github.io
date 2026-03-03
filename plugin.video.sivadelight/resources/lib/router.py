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
    # These headers are the "Key" to opening the door
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # We look for ANY link that contains an image - this is a "catch-all"
        # specifically designed for Tamil sites that change their tags often.
        items = soup.find_all('a')
        
        found = False
        for item in items:
            img = item.find('img')
            # We only want links that have an image (posters) and a title
            if img and (img.get('alt') or item.get('title')):
                title = img.get('alt') or item.get('title')
                movie_url = item.get('href')
                poster = img.get('data-src') or img.get('src')
                
                # Fix relative links
                if movie_url.startswith('/'): movie_url = url + movie_url
                if poster and poster.startswith('//'): poster = 'https:' + poster
                
                if 'http' in movie_url:
                    found = True
                    list_item = xbmcgui.ListItem(label=title)
                    list_item.setArt({'thumb': poster, 'poster': poster})
                    list_item.setInfo('video', {'title': title})
                    
                    # We will add playback in the next step once we see movies
                    xbmcplugin.addDirectoryItem(handle=handle, url=movie_url, listitem=list_item, isFolder=True)
        
        if not found:
            xbmcgui.Dialog().notification("SivaDelight", "No movies found on this page")

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", str(e))
    
    xbmcplugin.endOfDirectory(handle)

def add_directory_item(handle, name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    # This URL format is exactly how Deccan Delight does it
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=True)
