from webscrape2.constants import Source
from webscrape2.scraper import MangaScraper
from utils import Library, LIBRARY_PATH, ACTIVE_CHAPTER
from functools import partial
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.properties import Clock
import requests
import io

class InfoPage(BoxLayout):
    archived = BooleanProperty(False)
    chapter_list = ObjectProperty()
    manga_image_view = ObjectProperty()
    manga_title = StringProperty()

    nav_library_btn = ObjectProperty()
    manga = None
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
    def get_manga(self, url, source, *_):
        print(f"Opening -> {url} from {source}")
        self._clean_info()
        resp = requests.get(url)
        if not resp.ok:
            return None

        scraper = MangaScraper(source)
        scraper.markup = resp.text
        manga = scraper.manga

        resp = requests.get(manga.image_url)
        image_byte = resp.content if resp.ok else None

        Clock.schedule_once(partial(self._update_info, manga, image_byte, scraper), 0)

    def update_active_chapter(self, chapter_uid):
        """updates the mangas current `active_chapter` in the `library`"""

        library = Library.load(LIBRARY_PATH)
        if self.manga.url in library:
            print(f"Manga -> {self.manga.title} active chapter updated.")
            info = library[self.manga.url]

            if float(chapter_uid) > float(info[ACTIVE_CHAPTER]):
                Library(self.manga.url, self.manga.title, chapter_uid, self.manga.image_url).save(LIBRARY_PATH)

    def _clean_info(self):
        self.manga_title = "Loading..."
        self.manga_image_view.texture = None
        self.chapter_list.data = []

    def _remove_from_library(self):
        removed_info = Library.remove(self.manga.url, LIBRARY_PATH)
        self.archived = False
        print(f"Removed -> {removed_info}")

    def _add_to_library(self):
        Library(self.manga.url, self.manga.title, "0", self.manga.image_url).save(LIBRARY_PATH)
        self.archived = True

    def _update_info(self, manga, image_byte, scraper, *_):
        self.manga_title = manga.title
        self.manga = manga

        library = Library.load(LIBRARY_PATH)
        for url in library:
            if self.manga.url == url:
                self.archived = True
                break
            else: 
                self.archived = False

        ext = manga.image_url.split(".")[len(manga.image_url.split("."))-1]
        texture = CoreImage(io.BytesIO(image_byte), ext=ext).texture
        self.manga_image_view.texture = texture
        self.manga_image_view.size = texture.size
        
        for chapter in manga.chapters:
            self.chapter_list.data.append({"app": self.app, "text": f"({chapter.uid}){chapter.title}", "chapter": chapter, "scraper": scraper})