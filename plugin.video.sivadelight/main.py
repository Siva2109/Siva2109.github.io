import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup

HANDLE = int(sys.argv[1])
BASE_URL = "https://tamilyogi.plus/" # You can change this when domains change

def build_menu():
    # Folder for New Movies
    add_directory_item("Latest Tamil Movies", "scrape_site", BASE_URL + "category/tamil-new-movies/")
    xbmcplugin.endOfDirectory(HANDLE)

def scrape_movies(url):
    # This is the "Engine"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # This logic depends on the website's HTML structure
    for movie in soup.find_all('div', class_='cover'):
        title = movie.find('img')['alt']
        link = movie.find('a')['href']
        img = movie.find('img')['src']
        
        # Add the movie to the Kodi list
        add_video_item(title, link, img)
    
    xbmcplugin.endOfDirectory(HANDLE)

def add_directory_item(name, action, url):
    path = f"{sys.argv[0]}?action={action}&url={urllib.parse.quote_plus(url)}"
    list_item = xbmcgui.ListItem(label=name)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=path, listitem=list_item, isFolder=True)

def add_video_item(name, url, img):
    list_item = xbmcgui.ListItem(label=name)
    list_item.setArt({'thumb': img, 'icon': img})
    # This tells Kodi it's a playable video
    list_item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=False)

if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    action = params.get('action')
    url = params.get('url')

    if not action:
        build_menu()
    elif action == 'scrape_site':
        scrape_movies(url)
