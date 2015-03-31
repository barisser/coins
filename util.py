import requests
import json
import os

def shorten_url(long_url):
    url = "https://www.googleapis.com/urlshortener/v1/url?key=" + str(os.environ['GOOGLE_API_KEY'])
    d = {}
    h = {}
    h['content-type'] = "application/json"
    h = json.dumps(h)
    d['longUrl'] = long_url
    d = json.dumps(d)
    r = requests.post(url, data=d, headers={"content-type": "application/json"})
    return str(json.loads(r.content)['id'])
