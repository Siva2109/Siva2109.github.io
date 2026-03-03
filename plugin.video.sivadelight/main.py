import sys
from resources.lib.router import routing

# Pass the full plugin URL (sys.argv[0]) and the query string (sys.argv[2])
routing(sys.argv[2])
