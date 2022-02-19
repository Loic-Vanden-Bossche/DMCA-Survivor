from bs4 import BeautifulSoup
import urllib.request as urllib2
import os

class GoogleImageDownloader(object):
    _URL = "https://www.google.co.in/search?q={}&source=lnms&tbm=isch"
    _HEADERS = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }

    def __init__(self, directory, name):
        self.dl_dir = directory
        self.filename = name['id']
        if os.path.exists(os.path.join(self.dl_dir, f"{self.filename}.jpg")): return;
        self.url = self._URL.format(urllib2.quote(name['name']))
        self.initiate_downloads()

    def initiate_downloads(self):
        try:
            soup = BeautifulSoup(urllib2.urlopen(urllib2.Request(self.url, headers=self._HEADERS)), 'html.parser')
            self.save_image([img['src'] for img in soup.find_all('img') if img.has_attr("src") and 'https' in img['src']][0])
        except Exception as e:
            print("could not save image", e)

    def save_image(self, src):
        req = urllib2.Request(src, headers=self._HEADERS)
        raw_img = urllib2.urlopen(req).read()
        with open(os.path.join(self.dl_dir, f"{self.filename}.jpg"), 'wb') as f:
            f.write(raw_img)
