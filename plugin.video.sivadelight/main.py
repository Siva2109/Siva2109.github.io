import sys
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup

# This is the "ID" Kodi uses to track this menu
HANDLE = int(sys.argv[1])

def get_movies():
    url = 'https://tamilyogi.plus/' 
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # TamilYogi usually puts movies in 'video' class list items
        movies = soup.find_all('li', class_='video')
        
        for movie in movies:
            # Get the title and the link
            title_tag = movie.find('div', class_='title')
            link_tag = movie.find('a')
            img_tag = movie.find('img')
            
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = link_tag['href']
                thumb = img_tag['src'] if img_tag else ""
                
                list_item = xbmcgui.ListItem(label=title)
                list_item.setArt({'thumb': thumb, 'icon': thumb})
                list_item.setInfo('video', {'title': title, 'plot': 'TamilYogi Latest'})
                
                # isFolder=True because the movie page is another menu of quality links
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=link, listitem=list_item, isFolder=True)

    except Exception as e:
        xbmcgui.Dialog().ok("SivaDelight Error", str(e))

    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    get_movies()
