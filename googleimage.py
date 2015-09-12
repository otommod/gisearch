from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from operator import add
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup


# Large images:                     tbs=isz:l
# Medium images:                    tbs=isz:m
# Icon sized images:                tba=isz:i
# Image size larger than 400×300:   tbs=isz:lt,islt:qsvga
# Image size larger than 640×480:   tbs=isz:lt,islt:vga
# Image size larger than 800×600:   tbs=isz:lt,islt:svga
# Image size larger than 1024×768:  tbs=isz:lt,islt:xga
# Image size larger than 1600×1200: tbs=isz:lt,islt:2mp
# Image size larger than 2272×1704: tbs=isz:lt,islt:4mp
# Image sized exactly 1000×1000:    tbs=isz:ex,iszw:1000,iszh:1000
# Images in full color:             tbs=ic:color
# Images in black and white:        tbs=ic:gray
# Images that are red:              tbs=ic:specific,isc:red
#  [orange, yellow, green, teal, blue, purple, pink, white, gray, black, brown]
# Image type Face:                  tbs=itp:face
# Image type Photo:                 tbs=itp:photo
# Image type Clipart:               tbs=itp:clipart
# Image type Line drawing:          tbs=itp:lineart
# Group images by subject:          tbs=isg:to
# Show image sizes in search results: tbs=imgo:1

def _gisearch(query, start, num):
    r = requests.get("http://www.google.com/m", params={
        "tbm": "isch", "hl": "en", "q": query,
        "start": start, "num": num
    }, headers={
        "user-agent": "android"   # important!
    })
    r.raise_for_status()

    bs = BeautifulSoup(r.text)
    imgs = bs.select("a.image")
    qss = [urlparse(a["href"]).query for a in imgs]  # query strings
    urls = [parse_qs(q)["imgurl"][0] for q in qss]
    return urls


def gisearch(query, page=1, num=20):
    actual_num = min(num, 20)
    starts = range((page - 1) * num, page * num, actual_num)

    search = lambda start: _gisearch(query, start, actual_num)
    with ThreadPoolExecutor(max_workers=5) as executor:
        pages = executor.map(search, starts)
    # pages = [_gisearch(query, s, actual_num) for s in starts]
    return reduce(add, pages)
