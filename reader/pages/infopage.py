from webscrape2.constants import Source
from webscrape2.scraper import MangaScraper
from functools import partial
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import Clock
import requests
import io

class InfoPage(BoxLayout):
    chapter_list = ObjectProperty()
    manga_image_view = ObjectProperty()
    manga_title = StringProperty()

    nav_library_btn = ObjectProperty()

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
    def get_manga(self, url, source, *_):
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

    def _clean_info(self):
        self.manga_title = "Loading..."
        self.manga_image_view.texture = None
        self.chapter_list.data = []

    def _update_info(self, manga, image_byte, scraper, *_):
        self.manga_title = manga.title
        ext = manga.image_url.split(".")[len(manga.image_url.split("."))-1]
        texture = CoreImage(io.BytesIO(image_byte), ext=ext).texture
        self.manga_image_view.texture = texture
        self.manga_image_view.size = texture.size
        
        for chapter in manga.chapters:
            self.chapter_list.data.append({"app": self.app, "text": chapter.title, "chapter": chapter, "scraper": scraper})