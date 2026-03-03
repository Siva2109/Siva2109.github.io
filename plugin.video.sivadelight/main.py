import sys
import xbmcgui
import xbmcplugin
import requests
import urllib.parse
from bs4 import BeautifulSoup

HANDLE = int(sys.argv[1])

def get_movies(site_url, site_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(site_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # TamilBulb uses <article> tags for movie boxes
        items = soup.find_all('article')
        
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                # 1. Get the title from the image 'alt' text
                title = img_tag.get('alt') or link_tag.get('title') or "Unknown Movie"
                
                # 2. Get the link to the movie page
                link = link_tag['href']
                
                # 3. Get the poster image (checking for standard and lazy-load tags)
                thumb = img_tag.get('data-src') or img_tag.get('src')
                
                if thumb and thumb.startswith('//'):
                    thumb = 'https:' + thumb
                
                list_item = xbmcgui.ListItem(label=title)
                
                # 4. Set the Artwork (This fixes the missing posters)
                list_item.setArt({
                    'thumb': thumb,
                    'icon': thumb,
                    'poster': thumb
                })
                
                # Set basic info
                list_item.setInfo('video', {'title': title})
                
                # Add it to the list
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=link, listitem=list_item, isFolder=True)

    except Exception as e:
        xbmcgui.Dialog().notification("SivaDelight", "Scraper Error")

    xbmcplugin.endOfDirectory(HANDLE)

def main_menu():
    # Only TamilBulb for now to keep it simple and test the fix
    add_dir("TamilBulb Movies", "https://tamilbulb.cc/", "TamilBulb")
    xbmcplugin.endOfDirectory(HANDLE)

def add_dir(name, url, site):
    list_item = xbmcgui.ListItem(label=name)
    query = urllib.parse.urlencode({'url': url, 'site': site})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=True)

if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    if not params:
        main_menu()
    else:
        get_movies(params['url'], params['site'])
