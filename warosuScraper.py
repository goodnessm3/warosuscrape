import requests
from bs4 import BeautifulSoup
import re
import time
import random
import sys
import csv
import datetime
import os

DATE_FINDER = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
OLDEST = datetime.datetime.now()  # for finding the oldest file
FILENAME_GETTER = re.compile(r"File: [0-9.]+ (KB|MB), [0-9.x]+, (.+)")
SEARCH_BASE = '''https://warosu.org/vt/'''

GOOD_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 'Accept-Language': 'en-US,en;q=0.5',
 'Cache-Control': 'no-cache',
 'Connection': 'keep-alive',
 'Host': 'warosu.org',
 'Pragma': 'no-cache',
 'Priority': 'u=0, i',
 'Sec-Fetch-Dest': 'document',
 'Sec-Fetch-Mode': 'navigate',
 'Sec-Fetch-Site': 'none',
 'Sec-Fetch-User': '?1',
 'Upgrade-Insecure-Requests': '1',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0'}


def prepare_params(datefrom, dateto):

    """
    yyyy-mm-dd

    These are all the URL parameters for a Warosu search and their default values, we are
    specifying a date range and the text 'sound=' in the filename to find soundposts
    """

    return {"task":"search2",
            "ghost":False,
            "search_text":"",
            "search_subject":"",
            "search_username":"",
            "search_tripcode":"",
            "search_email":"",
            "search_filename":"sound=",
            "search_datefrom":datefrom,
            "search_dateto":dateto,
            "search_media_hash":"",
            "search_op":"all",
            "search_del":"dontcare",
            "search_int":"dontcare",
            "search_ord":"new",
            "search_capcode":"all",
            "search_res":"post",
             "offset":0}


def thumb_from_a(a):

    """Inspect 'a' elements and if it's a link to a thumbnail, return the thumbnail link"""

    thumb = None

    if a.contents and len(a.contents) > 2:
        middle = a.contents[1]
        thumb = middle.get("src")

    return thumb


def extract_info(reply):

    out = {}

    for q in reply.find_all("a"):
        lnk = q.get("href")
        if lnk.startswith("https://i.warosu.org"):
            out["image"] = lnk
        elif lnk.startswith("/vt/thread/"):
            out["thread"] = lnk
        if t:= thumb_from_a(q):
            out["thumb"] = t
    fn = reply.find("span", {"class": "fileinfo break-all"}).getText()
    filename = FILENAME_GETTER.search(fn).groups()[1].strip()
    out["filename"] = filename

    dat = reply.find("span", {"class": "posttime"}).getText()
    out["date"] = dat

    return out


def get_all_results(params):

    out = []

    while 1:
        time.sleep(random.random() * 10)
        resp = requests.get(SEARCH_BASE, params=params, headers=GOOD_HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        fnd = soup.find_all("td", {"class": "comment reply"})
        if not fnd:
            break
        out.extend(fnd)
        params["offset"] += len(fnd)

    return out


if __name__ == "__main__":

    # first, find the oldest dated csv file in the curred directory, we are working backwards
    for x in os.listdir():
        if DATE_FINDER.search(x):
            dat, _ = os.path.splitext(x)
            dt = datetime.datetime.fromisoformat(dat)
            if dt < OLDEST:
                OLDEST = dt

    to_get = OLDEST - datetime.timedelta(days=1)  # go back in time 1 day
    datefrom = to_get.strftime("%Y-%m-%d")
    dateto = OLDEST.strftime("%Y-%m-%d")  # go up to the previous day we found

    print(f"Downloading soundposts from {datefrom} to {dateto}")

    res = get_all_results(prepare_params(datefrom, dateto))

    print(f"Found {len(res)} results. Writing csv")

    with open(f"{datefrom}.csv", "w", newline="", encoding="UTF-8") as f:
        wrt = csv.DictWriter(f,
                             fieldnames=["thread", "image", "filename", "date", "thumb"],
                             delimiter="\x1E")  # ASCII record separator character
        wrt.writeheader()

        for q in res:
            infos = extract_info(q)
            wrt.writerow(infos)
