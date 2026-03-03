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
        items = soup.find_all('article')
        
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            if link_tag and img_tag:
                title = img_tag.get('alt') or link_tag.get('title') or "Movie"
                link = link_tag['href']
                thumb = img_tag.get('data-src') or img_tag.get('src')
                
                list_item = xbmcgui.ListItem(label=title)
                list_item.setArt({'thumb': thumb, 'icon': thumb, 'poster': thumb})
                list_item.setInfo('video', {'title': title})
                
                # IMPORTANT CHANGE: We tell Kodi this item is PLAYABLE
                list_item.setProperty('IsPlayable', 'true')
                
                # Create a link that points back to our "play" mode
                query = urllib.parse.urlencode({'mode': 'play', 'url': link})
                u = f"{sys.argv[0]}?{query}"
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=False)

    except Exception as e:
        xbmcgui.Dialog().notification("SivaDelight", "Scraper Error")
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(video_url):
    # This is the "Magic" part used by Deccan Delight
    # It sends the website link to ResolveURL to get the real video file
    try:
        resolved_link = resolveurl.resolve(video_url)
        if resolved_link:
            play_item = xbmcgui.ListItem(path=resolved_link)
            xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)
        else:
            xbmcgui.Dialog().ok("SivaDelight", "Could not resolve video link.")
    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight", f"Play Error: {str(e)}")

if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    mode = params.get('mode')
    
    if not mode:
        # Show the main menu (TamilBulb)
        list_item = xbmcgui.ListItem(label="TamilBulb Movies")
        query = urllib.parse.urlencode({'mode': 'list', 'url': 'https://tamilbulb.cc/'})
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=f"{sys.argv[0]}?{query}", listitem=list_item, isFolder=True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif mode == 'list':
        get_movies(params['url'], "TamilBulb")
    elif mode == 'play':
        play_video(params['url'])
