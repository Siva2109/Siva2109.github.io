import sys
import xbmcgui
import xbmcplugin
import requests
import urllib.parse
from bs4 import BeautifulSoup

# Try importing ResolveURL, but don't crash if it's not installed yet
try:
    import resolveurl
except ImportError:
    resolveurl = None

HANDLE = int(sys.argv[1])

def get_movies(site_url, site_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(site_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This searches for common movie container tags on both TamilBulb and TamilGun
        items = soup.find_all(['article', 'div'], class_=['video', 'v-item', 'post', 'ml-item'])
        
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                # Get Title (usually from the image 'alt' or link 'title')
                title = img_tag.get('alt') or link_tag.get('title') or "Movie"
                
                # Get Movie Page Link
                link = link_tag['href']
                
                # Get Poster (checking standard 'src' and lazy-load 'data-src')
                thumb = img_tag.get('data-src') or img_tag.get('src')
                
                # Fix relative image URLs
                if thumb and thumb.startswith('//'):
                    thumb = 'https:' + thumb
                
                list_item = xbmcgui.ListItem(label=title)
                
                # Set Artwork
                list_item.setArt({
                    'thumb': thumb,
                    'icon': thumb,
                    'poster': thumb
                })
                
                # Set Video Info
                list_item.setInfo('video', {'title': title})
                
                # Mark as Playable for ResolveURL
                list_item.setProperty('IsPlayable', 'true')
                
                # Link to the 'play' mode
                query = urllib.parse.urlencode({'mode': 'play', 'url': link})
                u = f"{sys.argv[0]}?{query}"
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=False)

    except Exception as e:
        xbmcgui.Dialog().notification("SivaDelight", "Error loading movies")

    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_url):
    if not resolveurl:
        xbmcgui.Dialog().ok("SivaDelight", "ResolveURL is missing. Please install a repository like Gujal to get it.")
        return

    try:
        # Resolve the website link into a direct video stream
        resolved_link = resolveurl.resolve(video_url)
        if resolved_link:
            play_item = xbmcgui.ListItem(path=resolved_link)
            xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)
        else:
            xbmcgui.Dialog().notification("SivaDelight", "Could not resolve video link.")
    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight", "Playback Error")

def main_menu():
    # Setup the Home Screen folders
    add_menu_item("TamilGun Movies", "https://tamilgun.now/", "list")
    add_menu_item("TamilBulb Movies", "https://tamilbulb.cc/", "list")
    xbmcplugin.endOfDirectory(HANDLE)

def add_menu_item(name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=True)

if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    mode = params.get('mode')
    
    if not mode:
        main_menu()
    elif mode == 'list':
        get_movies(params['url'], "Movies")
    elif mode == 'play':
        play_video(params['url'])
