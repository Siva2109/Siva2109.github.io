import sys
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup

# Kodi uses this ID to manage the menu
HANDLE = int(sys.argv[1])

def get_movies():
    # Using the current active domain
    url = 'https://tamilyogi.plus/' 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # Ensures Tamil characters display correctly
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This looks for the 'v-item' or 'video' blocks common in their current theme
        # We look for all links that contain movie titles
        items = soup.find_all('li', class_='video') or soup.find_all('div', class_='v-item')
        
        if not items:
            # Fallback: Just find all links that look like movie posts
            items = soup.find_all('a', rel='bookmark')

        for item in items:
            # If we found an <li>, look for the <a> inside it
            link_tag = item if item.name == 'a' else item.find('a')
            img_tag = item.find('img')
            
            if link_tag and link_tag.get('href'):
                title = link_tag.get('title') or link_tag.text.strip()
                link = link_tag['href']
                thumb = img_tag['src'] if img_tag else ""
                
                # Create the item in Kodi
                list_item = xbmcgui.ListItem(label=title)
                list_item.setArt({'thumb': thumb, 'icon': thumb})
                list_item.setInfo('video', {'title': title, 'plot': 'TamilYogi Latest Movies'})
                
                # isFolder=True because clicking a movie usually opens a page with play links
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=link, listitem=list_item, isFolder=True)

    except Exception as e:
        xbmcgui.Dialog().notification("SivaDelight", "Error: " + str(e), xbmcgui.NOTIFICATION_ERROR, 5000)

    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    get_movies()
