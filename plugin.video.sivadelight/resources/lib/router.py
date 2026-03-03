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
        
        # Based on your screenshot, TamilGun uses 'div' with classes like 'post' or 'ml-item'
        # We search for these specific containers
        items = soup.find_all('div', class_=['post', 'ml-item', 'v-item'])
        
        found_count = 0
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                movie_url = link_tag.get('href')
                # Get the title from the image 'alt' or the text below it
                title = img_tag.get('alt') or item.find('h3').text.strip() if item.find('h3') else "Movie"
                poster = img_tag.get('src') or img_tag.get('data-src')

                if movie_url and movie_url.startswith('http'):
                    found_count += 1
                    list_item = xbmcgui.ListItem(label=title)
                    list_item.setArt({'thumb': poster, 'poster': poster, 'icon': poster})
                    list_item.setInfo('video', {'title': title})
                    
                    # Point to the movie page
                    xbmcplugin.addDirectoryItem(handle=handle, url=movie_url, listitem=list_item, isFolder=True)
        
        if found_count == 0:
            xbmcgui.Dialog().notification("SivaDelight", "Gallery Empty - Trying legacy search...")

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", str(e))
    
    xbmcplugin.endOfDirectory(handle)

def add_directory_item(handle, name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"plugin://plugin.video.sivadelight/?{query}"
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=list_item, isFolder=True)
