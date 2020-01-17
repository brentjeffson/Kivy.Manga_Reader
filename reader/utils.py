from pathlib import Path
from os import path, stat
import requests


BASE_DIR = path.dirname(__file__)
LAYOUT_DIR = path.join(BASE_DIR, "layouts")

class Download:
    URL = "url"
    SIZE = "size"
    CONTENT_LENGTH = "content-length"
    TIMESTAMP = "timestamp"
    RESUMABLE = "resumable"
    
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
                    Download.URL: self.url,
                    Download.SIZE: self.size,
                    Download.CONTENT_LENGTH: self.content_length,
                    Download.RESUMABLE: self.resumable,
                    Download.TIMESTAMP: self.timestamp,
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




        