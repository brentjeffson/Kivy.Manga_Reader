from pathlib import Path
from os import path, stat
import requests


BASE_DIR = path.dirname(__file__)
LAYOUT_DIR = path.join(BASE_DIR, "layouts")

class Download:
    
    def __init__(self, url, filename, content_length, resumable, timestamp):
        self._url = url
        self._filename = filename
        self._content_length = content_length
        self._resumable = resumable
        self._timestamp = timestamp
        
    def __str__(self):
        return f"{self.filename}()"
    
    @staticmethod
    def dictionary(download):
        return {download.filename: {
                    "url": download.url,
                    "size": download.size,
                    "content-length": download.content_length,
                    "resumable": download.resumable,
                    "timestamp": download.timestamp,
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
        if self._filename is None:
            if self._url[-1] == "":
                self._url = self._url[:-1]
            split = self.url.split("/")
            return split[len(split)-1]

        return self._filename

    @property
    def size(self):
        if not Path(self.filename).exists():
            return False
        return os.stat(self.filename).st_size
    
    @property
    def extension(self):
        split = self.filename.split(".")
        return split[len(split)-1]
    
    @staticmethod
    def download(url, filename=None, headers={}, chunk_size=1024):
        mode = "ab"
        resp = requests.get(url, headers=headers)

        if not resp.ok:
            return None

        content_length = int(resp.headers["content-length"])
        filename = parse_filename(url) if filename is None else filename
        if Path(filename).exists() and "accept-ranges" in resp.headers:
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
    def save(settings_file, downloads, mode="w"):
        unlisted_downloads = {}
        for download in downloads:
            unlisted_downloads[download.filename] = {
                "url": download.url,
                "size": download.size,
                "content-length": download.content_length,
                "resumable": download.resumable,
                "timestamp": download.timestamp,
            }
                
        with open(settings_file, mode) as f:
            json.dump(unlisted_downloads, f)            
    
    @staticmethod
    def load(settings_file):
    
        if not Path(settings_file).exists():
            create_file(settings_file)
            return None

        download_settings = {}
        with open(settings_file, "rt") as f:
            download_settings = json.loads(f.read())

        if len(download_settings) == 0: # check if something was read.
            return None

        return download_settings