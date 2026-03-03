import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
import urllib.parse

def routing(params, handle):
    mode = params.get('mode')
    if not mode:
        # POINT DIRECTLY TO THE MOVIE GALLERY
        add_directory_item(handle, "TamilGun Latest Movies", "https://tamilgun.now/movies.html", "list")
        add_directory_item(handle, "TamilBulb Movies", "https://tamilbulb.cc/", "list")
        xbmcplugin.endOfDirectory(handle)
    elif mode == 'list':
        scrape_movies(params['url'], handle)

def scrape_movies(url, handle):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://tamilgun.now/'
    }
    
    try:
        r = session.get(url, headers=headers, timeout=15, verify=False)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # UNIVERSAL SEARCH: Look for all links (<a>) that contain an image (<img>)
        # This bypasses the need for specific class names like 'post'
        items = soup.find_all('a')
        
        found_count = 0
        for item in items:
            img = item.find('img')
            # Check if this link looks like a movie entry
            if img and item.get('href') and ('/video/' in item.get('href') or 'tamilgun' in item.get('href')):
                title = img.get('alt') or item.get('title') or "Untitled Movie"
                # Skip tiny buttons or icons
                if len(title) < 5: continue
                
                movie_url = item.get('href')
                poster = img.get('src') or img.get('data-src')

                # Fix relative URLs
                if movie_url.startswith('/'): movie_url = 'https://tamilgun.now' + movie_url
                if poster and poster.startswith('//'): poster = 'https:' + poster

                found_count += 1
                list_item = xbmcgui.ListItem(label=title)
                list_item.setArt({'thumb': poster, 'poster': poster, 'icon': poster})
                list_item.setInfo('video', {'title': title})
                
                xbmcplugin.addDirectoryItem(handle=handle, url=movie_url, listitem=list_item, isFolder=True)
        
        if found_count == 0:
            xbmcgui.Dialog().ok("SivaDelight", "No items found. The site layout might have changed.")

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", str(e))
    
    xbmcplugin.endOfDirectory(handle)

def add_directory_item(handle, name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=True)
