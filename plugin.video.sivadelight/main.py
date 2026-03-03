import sys
import xbmcgui
import xbmcplugin
import requests
import urllib.parse
from bs4 import BeautifulSoup

# Get the handle ID for the Kodi menu
HANDLE = int(sys.argv[1])

def get_movies(site_url, site_name):
    # This 'User-Agent' makes you look like a real Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(site_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for movie items (Common tags for both sites)
        items = soup.find_all('article') or soup.find_all('li', class_='video') or soup.find_all('div', class_='v-item')
        
        for item in items:
            link_tag = item.find('a')
            img_tag = item.find('img')
            
            if link_tag and img_tag:
                title = img_tag.get('alt') or link_tag.get('title') or "Movie"
                link = link_tag['href']
                thumb = img_tag['src']
                
                # Fix relative image links
                if thumb.startswith('//'): thumb = 'https:' + thumb
                
                list_item = xbmcgui.ListItem(label=f"[{site_name}] {title}")
                list_item.setArt({'thumb': thumb, 'icon': thumb, 'poster': thumb})
                list_item.setInfo('video', {'title': title})
                
                # For now, link doesn't play yet, just opens the site page
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=link, listitem=list_item, isFolder=True)

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", f"Failed to load {site_name}: {str(e)}")

    xbmcplugin.endOfDirectory(HANDLE)

def main_menu():
    # This creates the main selection screen
    add_dir("TamilBulb Movies (Test Site)", "https://tamilbulb.cc/", "TamilBulb")
    add_dir("TamilYogi Movies", "https://tamilyogi.plus/", "TamilYogi")
    xbmcplugin.endOfDirectory(HANDLE)

def add_dir(name, url, site):
    # This adds a clickable folder to the Kodi UI
    list_item = xbmcgui.ListItem(label=name)
    # This builds the internal Kodi URL to tell it what site was picked
    query = urllib.parse.urlencode({'url': url, 'site': site})
    u = f"{sys.argv[0]}?{query}"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=u, listitem=list_item, isFolder=True)

if __name__ == '__main__':
    # Logic to check if we are on the Home Menu or inside a Movie List
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    
    if not params:
        main_menu()
    else:
        get_movies(params['url'], params['site'])
