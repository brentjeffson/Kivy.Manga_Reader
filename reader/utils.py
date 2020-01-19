from pathlib import Path
import os
import json
import requests

BASE_DIR = os.path.dirname(__file__)
LAYOUT_DIR = os.path.join(BASE_DIR, "layouts")

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

#class Download:
    
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
            filesize = os.stat(filename).st_size
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


class Download:
    URL = "url"
    RESUMABLE = "resumable"
    FILENAME = "filename"
    RAWBYTES = "rawbytes"
    DIRECTORY = "directory"
    CONTENT_LENGTH = "filesize"
    
    def __init__(self, url, directory=".", content_length=-1, resumable=False, filename=None):
        self._url = url
        self._directory = directory
        self._resumable = resumable
        self._filename = filename
        self._content_length = content_length
    
    def get(self, cancel_download=None, headers={}, params={}, chunk_size=1024):
        try: 
            download = Download._get(self, cancel_download=cancel_download, headers={}, params={}, chunk_size=1024)
        except FileDownloadedException as e:
            downloads = Download.load(path)
            if self.url in downloads:
                Download._remove(self.url, path)
            return self
        else:
            return download
            
        
    def save(self, path):
        if Path(self.filename).exists() and self.filesize == self.content_length and self.url in Download.load(path):
            Download._remove(self.url, path)
            return
        elif self.resumable:
            Download._save(self, path)
        
                
    @staticmethod
    def load(path):
        if not Path(path).exists():
            Path(path).touch()
            return {}
        if os.stat(path).st_size <= 0:
            return {}
        with open(path, "rt") as f:  
            downloads = json.loads(f.read())
        return downloads
    
    @staticmethod
    def parse_filename(url):
        extensions = ["co", "org", "us", "com", "gov", "corp", "net", "int", 
                      "mil", "edu", "gov", "ru", "biz", "info", "jobs", "mobi",
                      "name", "ly", "tel", "kitchen", "email", "tech", "state",
                      "xyz", "codes", "bargains", "bid", "expert", "io"
                     ]
        while url[-1] == "/":
            url = url[:-1]
        filename = url.split("/")[len(url.split("/"))-1]
        ext = filename.split(".")[len(filename.split("."))-1]
        if ext in extensions:
            filename += ".html"
        
        return filename        
                
    @staticmethod
    def _remove(url_to_remove, path):
        downloads = Download.load(path)
        downloads.pop(url_to_remove)
        
        if len(downloads) == 0:
            Download._clear(path)
            return downloads
        
        for url in downloads:
            download = downloads[url]
            Download._save(
                Download(url, download[Download.DIRECTORY], download[Download.CONTENT_LENGTH], download[Download.RESUMABLE]),
                path
            )
        
        return downloads
    
    @staticmethod
    def _clear(path):
        try: 
            with open(path, "wt+") as f:
                f.write("")
            return True
        except:
            return False
    
    @staticmethod
    def _get(download, cancel_download=None, headers={}, params={}, chunk_size=1024):
        global CANCEL
        tstart = time.time()
        mode = "ab"

        if Path(download.filename).exists():
            print(f"File Found: `{download.filename}`")
            
            if download.content_length == -1:
                resp = requests.get(download.url, headers=headers, params=params)     
        
                if not resp.ok:
                    return None
                
                content_length = int(resp.headers["content-length"]) if "content-length" in resp.headers else -1
                resumable =  True if "accept-ranges" in resp.headers else False
                
                if download.filesize >= content_length:
                    print(f"File Already Downloaded -> lsize:{download.filesize} - rsize:{content_length}")
                    raise FileDownloadedException(f"File Already Downloaded -> lsize:{download.filesize} - rsize:{content_length}")
            
            print(f"Resuming Download: {download.filesize}-{content_length}")
            headers.update({"range": f"bytes={download.filesize}-{content_length}"})
        
        resp = requests.get(download.url, headers=headers, params=params)     
        if resp.ok:
            if "range" not in resp.request.headers:
                content_length = int(resp.headers["content-length"]) if "content-length" in resp.headers else -1
            resumable =  True if "accept-ranges" in resp.headers else False
            print(f"Downloading: {download.filename} -> lsize:{download.filesize if Path(download.filename).exists() else 0} - rsize:{content_length}")
            
            with open(download.filename, mode) as f:
                size_downloaded = 0
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    
#                     if cancel_download is not None:
#                         if cancel_download():
                    if CANCEL:
                        print(f"Cancelling Download: Downloaded {size_downloaded}/{content_length}:{(size_downloaded/content_length)*100}%")
                        return Download(url=download.url, directory=download.directory, content_length=content_length, resumable=resumable)
                            
                    
                    f.write(chunk)
                    size_downloaded += len(chunk)
       
        
        tend = time.time()
        print(f"Succesfully Downloaded: {download.filename}:{(size_downloaded/content_length)*100}%")
        print(f"Download Time: {tend-tstart}s")
        return Download(url=download.url, directory=download.directory, content_length=content_length, resumable=resumable)
    
    @staticmethod
    def _save(download, path):
        downloads = Download.load(path)
        downloads.update({download.url: {
                Download.DIRECTORY: download.directory, 
                Download.RESUMABLE: download.resumable,
                Download.FILENAME: download.filename,
                Download.CONTENT_LENGTH: download.content_length
            }
        })
        with open(path, "wt") as f:
            f.write(json.dumps(downloads, indent=4))
        print(f"Download Info Saved: {download.url} Saved To File {path}")
    
    @property
    def url(self):
        return self._url
    
    @property
    def directory(self):
        return self._directory
    
    @property
    def resumable(self):
        return self._resumable
    
    @property
    def filename(self):
        if self._filename != None:
            return self._filename
        return self.parse_filename(self.url)
    
    @property
    def filesize(self):
        return Path(self.filename).stat().st_size
    
    @property
    def content_length(self):
        return self._content_length


class Library:
    
    def __init__(self, url, title, active_chapter, image_url):
        self._url = url
        self._title = title
        self._active_chapter = active_chapter
        self._image_url = image_url

    @staticmethod
    def clear(path):
        """Clears all records from the given path
        
        Args:
            path (str): Required path to the records file.

        Returns:
            bool: `True` for success, `False` otherwise.
        """
        try: 
            with open(path, "wt") as f:
                f.write("")
            return True
        except:
            return False
        
    @staticmethod
    def remove(url_to_remove, path):
        """removes records of `url_to_remove` from the given path

        Args:
            url_to_remove (str): Required to use as reference for removing 
            path (str): Required path to the records file
            
        Returns:
            dict: returns empty `dict` if nothing was removed or returns the removed `dict` records
        """
        library = Library.load(path)
        removed_library = {}
        for url in library:
            if url == url_to_remove:
                removed_library = library.get(url)
                library.pop(url)
                break
                
        Library.clear(path)
        
        for url in library:
            info = library[url]
            print(info)
            Library(url, info[TITLE], info[ACTIVE_CHAPTER], info[IMAGE_URL]).save(path)
        return removed_library
    
    @staticmethod
    def load(path):
        """loads the specified `path`, returns an empty dict if file exists or has no content, otherwise returns the manga information
        
        :params str path: directy path to the file containing library information

        :returns: a dict of information
        :rtype: dict
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

        