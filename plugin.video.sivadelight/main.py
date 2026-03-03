import sys
import urllib.parse
from resources.lib import router

# The 'HANDLE' is the unique ID Kodi gives this specific window
HANDLE = int(sys.argv[1])

if __name__ == '__main__':
    # We take the 'query string' (the URL parameters) and send them to the router
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if sys.argv[2] else {}
    router.routing(params, HANDLE)
