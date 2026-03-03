import sys
import xbmcgui
import xbmcplugin
import requests
import urllib.parse
from bs4 import BeautifulSoup
import resolveurl

HANDLE = int(sys.argv[1])

def get_movies(site_url, site_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    try:
        response = requests.get(site_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This looks for movie items on both TamilBulb and TamilGun
        items = soup.find_all(['article', 'div'], class_=['video', 'v-item', 'post'])
        
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            if link_tag and img_tag:
                title = img_tag.get('alt') or link_tag.get('title') or "Movie"
                link = link_tag['href']
                thumb = img_tag.get('data-src') or img_tag.get('src')
                
                # Fix image links
                if thumb and thumb.startswith('//'): thumb = 'https:' + thumb
                
                list_item = xbmcgui.ListItem(label=f"[{site_name}] {title}")
                list_item.setArt({'thumb': thumb, 'icon': thumb, 'poster': thumb})
                list_item.setInfo('video', {'title': title})
                list_item.setProperty('IsPlayable', 'true')
                
                query = urllib.parse.urlencode({'mode': 'play', 'url': link})
                u = f"{sys.argv[0]}?{query}"
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=False)
    except:
        xbmcgui.Dialog().notification("SivaDelight", "Error loading site")
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_url):
    # This sends the link to ResolveURL. 
    # TIP: If it fails, try clicking a different movie; some links expire!
    try:
        resolved_link = resolveurl.resolve(video_url)
        if resolved_link:
            play_item = xbmcgui.ListItem(path=resolved_link)
            xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)
        else:
            xbmcgui.Dialog().ok("SivaDelight", "Video link not supported yet.")
    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight", "Playback Error")

if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    mode = params.get('mode')
    
    if not mode:
        # MAIN MENU: Now with TamilGun!
        add_menu_item("TamilGun (New)", "https://tamilgun.now/", "list")
        add_menu_item("TamilBulb", "https://tamilbulb.cc/", "list")
        xbmcplugin.endOfDirectory(HANDLE)
    elif mode == 'list':
        get_movies(params['url'], "Movies")
    elif mode == 'play':
        play_video(params['url'])

def add_menu_item(name, url, mode):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'mode': mode, 'url': url})
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=f"{sys.argv[0]}?{query}", listitem=list_item, isFolder=True)
