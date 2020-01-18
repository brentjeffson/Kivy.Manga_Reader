from pathlib import Path
from os import path, stat
import requests

BASE_DIR = path.dirname(__file__)
LAYOUT_DIR = path.join(BASE_DIR, "layouts")

LIBRARY_PATH = "library.json"
DOWNLOAD_SETTINGS_PATH = "download_settings.json"

URL = "url"
TITLE = "title"
SIZE = "size"
ACTIVE_CHAPTER = "active_chapter"
IMAGE_URL = "image_url"
CONTENT_LENGTH = "content-length"
TIMESTAMP = "timestamp"
RESUMABLE = "resumable"

def check_file(path):
    """check if file exists, returns None if path did not exist, returns False if it has no content but file exist."""
    if not Path(path).exists():
        open(path, "a+").close()
        return None
    
    if os.stat(path).st_size <= 0:
        return False
    
    return True

class Download:
    
    def __init__(self, url, filename, content_length, resumable, timestamp):
        self._url = url
        self._filename = filename
        self._content_length = content_length
        self._resumable = resumable
        self._timestamp = timestamp
        
    def __str__(self):
        return f"{self.filename}()"
    
    def update_settings(self, filename):
        downloads = Download.load(filename)
        downloads.update(self.dictionary())
        Download.save(filename, downloads)
        return self
    
    def dictionary(self):
        """convert Download Object into a dictionary"""
        return {self.filename: {
                    URL: self.url,
                    SIZE: self.size,
                    CONTENT_LENGTH: self.content_length,
                    RESUMABLE: self.resumable,
                    TIMESTAMP: self.timestamp,
                }}
        
    @property
    def url(self):
        return self._url
    
    @property
    def content_length(self):
        return self._content_length
    
    @property
    def resumable(self):
        return self._resumable
    
    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def filename(self):
        return self.parse_filename(self.url)

    @property
    def size(self):
        if not Path(self.filename).exists():
            return -1
        return os.stat(self.filename).st_size
    
    @property
    def extension(self):
        split = self.filename.split(".")
        return split[len(split)-1]
    
    @staticmethod
    def parse_filename(url):
        extensions = ["co", "org", "us", "com", "gov", "corp", "net", "int", 
                      "mil", "edu", "gov", "ru", "biz", "info", "jobs", "mobi",
                      "name", "ly", "tel", "kitchen", "email", "tech", "state",
                      "xyz", "codes", "bargains", "bid", "expert"
                     ]
        while url[-1] == "/":
            url = url[:-1]
        filename = url.split("/")[len(url.split("/"))-1]
        ext = filename.split(".")[len(filename.split("."))-1]
        if ext in extensions:
            filename += ".html"
        
        return filename
    
    @staticmethod
    def download(url, filename=None, headers={}, chunk_size=1024):
        mode = "ab"
        resp = requests.get(url, headers=headers)

        if not resp.ok:
            return None

        content_length = int(resp.headers["content-length"])
        resumable = "accept-ranges" in resp.headers
        filename = Download.parse_filename(url) if filename is None else filename
    
        download = Download(url, filename, content_length, resumable, time.time()).update_settings("download_settings.json")
        
        if Path(filename).exists() and resumable:
            filesize = stat(filename).st_size
            if content_length > filesize:
                print("Resuming Download...")
                headers['range'] = f"bytes={filesize}-{content_length}"
                resp = requests.get(url, headers=headers)
                if not resp.ok:
                    return None

        with open(filename, mode) as f:
            print(f"Downloading -> {filename}")
            for chunk in resp.iter_content(chunk_size=chunk_size):
                f.write(chunk)     
        return True, 
    
    @staticmethod 
    def save(settings_file, downloads):                
        with open(settings_file, "wt") as f:
            f.write(json.dumps(downloads, indent=4))
    
    @staticmethod
    def load(settings_file):
    
        if not Path(settings_file).exists():
            create_file(settings_file)
            return {}

        if not os.stat(settings_file).st_size > 0:
            return {}
        
        download_settings = {}
        with open(settings_file, "rt") as f:
            download_settings = json.loads(f.read())

        if len(download_settings) == 0: # check if something was read.
            return None

        return download_settings


class Library:
    
    def __init__(self, url, title, active_chapter, image_url):
        self._url = url
        self._title = title
        self._active_chapter = active_chapter
        self._image_url = image_url
    
    @staticmethod
    def load(path):
        """loads the specified `path`, returns an empty dict if file exists or has no content, otherwise returns the manga information
        
        :params str path: directy path to the file containing library information

        :returns:
        :rtype:
        """
        chk_result = check_file(path)
        if chk_result == None or chk_result == False:
            return {}
            
        with open(path, "rt") as f:
            return json.loads(f.read())          
            
    def save(self, path):
        """save current object to the specified path, return True if success else False"""
        items = self.load(path)
        item = {self.url:{
            TITLE: self.title,
            ACTIVE_CHAPTER: self.active_chapter,
            IMAGE_URL: self.image_url
        }}
        items.update(item)
        with open(path, "wt") as f:
            f.write(json.dumps(items, indent=4))
        return True
    
    @property
    def url(self):
        return self._url
    
    @property
    def title(self):
        return self._title
    
    @property
    def active_chapter(self):
        return self._active_chapter
    
    @property
    def image_url(self):
        return self._image_url

        