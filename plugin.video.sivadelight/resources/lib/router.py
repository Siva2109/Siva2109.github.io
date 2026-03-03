import sys
import re
import requests
import xbmcgui
import xbmcplugin
import xbmcaddon
import resolveurl

BASE_URL = "https://tamilgun.now" # Update this if the site changes domain
HANDLE = int(sys.argv[1])

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    return requests.get(url, headers=headers).text

def routing(query):
    # Default view: List Latest Movies
    if not query:
        list_movies(BASE_URL + "/movies.html")
    
    # If a movie is clicked, the query will look like "?action=play&url=..."
    elif "action=play" in query:
        params = dict(re.findall(r'(\w+)=([^&]+)', query))
        play_movie(params['url'])

def list_movies(url):
    html = get_html(url)
    # This Regex targets the common thumbnail pattern on TamilGun
    # It looks for the movie link, title, and image within the main grid
    pattern = r'<div class="thumb">.*?<a href="(.*?)".*?title="(.*?)".*?<img src="(.*?)"'
    movies = re.findall(pattern, html, re.DOTALL)

    for link, title, img in movies:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'thumb': img, 'icon': img})
        list_item.setInfo('video', {'title': title})
        list_item.setProperty('IsPlayable', 'true')
        
        # Route the click back to our play function
        path = f"{sys.argv[0]}?action=play&url={link}"
        xbmcplugin.addDirectoryItem(HANDLE, path, list_item, isFolder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def play_movie(url):
    xbmcgui.Dialog().notification("Deccan logic", "Extracting stream...", xbmcgui.NOTIFICATION_INFO, 2000)
    html = get_html(url)
    
    # TamilGun uses iframes or buttons for hosts like 'streamwire', 'videobin', etc.
    # We need to find the link to the actual video hoster.
    video_links = re.findall(r'href="(https?://(?:streamwire|mixdrop|dood|voe)\.[a-z0-9/._-]+)"', html)
    
    if not video_links:
        # Fallback: check for iframe players if direct buttons aren't found
        video_links = re.findall(r'iframe.*?src="(.*?)"', html)

    stream_url = ""
    for v_url in video_links:
        if resolveurl.HostedMediaFile(v_url).valid_url():
            stream_url = resolveurl.resolve(v_url)
            if stream_url:
                break

    if stream_url:
        list_item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(HANDLE, True, list_item)
    else:
        xbmcgui.Dialog().ok("Error", "No playable stream found on this page.")
