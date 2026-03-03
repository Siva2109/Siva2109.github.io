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
    # Create a session to keep cookies (like a real browser)
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': url
    }
    
    try:
        # verify=False helps if the site has SSL certificate issues
        r = session.get(url, headers=headers, timeout=15, verify=False)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # This looks for any link (a) that contains an image (img)
        # Most movie sites use this structure for their grids
        items = soup.find_all('a')
        
        found_count = 0
        for item in items:
            img = item.find('img')
            movie_url = item.get('href')
            
            if img and movie_url and movie_url.startswith('http'):
                # Try to get the title from multiple places
                title = img.get('alt') or item.get('title') or img.get('title')
                
                if title and len(title) > 3: # Ignore tiny icons/buttons
                    poster = img.get('data-src') or img.get('src')
                    
                    if poster and poster.startswith('//'): 
                        poster = 'https:' + poster
                    
                    found_count += 1
                    list_item = xbmcgui.ListItem(label=title)
                    list_item.setArt({'thumb': poster, 'poster': poster, 'icon': poster})
                    list_item.setInfo('video', {'title': title})
                    
                    # For now, we keep isFolder=True to see if the content populates
                    xbmcplugin.addDirectoryItem(handle=handle, url=movie_url, listitem=list_item, isFolder=True)
        
        if found_count == 0:
            xbmcgui.Dialog().notification("SivaDelight", "No movies found. Check site manually.")

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", f"Connection Failed: {str(e)}")
    
    xbmcplugin.endOfDirectory(handle)

def add_directory_item(handle, name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=True)
