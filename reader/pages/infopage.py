from webscrape2.constants import Source
from webscrape2.scraper import MangaScraper
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import Clock
import requests

class InfoPage(BoxLayout):
    chapter_list = ObjectProperty()
    manga_title = StringProperty()

    nav_library_btn = ObjectProperty()

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        
    def get_manga(self, url, source, *_):
        sources = {
            "Manganelo": Source.MANGANELO,
            "Mangakakalot": Source.MANGAKAKALOT,
            "LeviatanScans": Source.LEVIATANSCANS,
        }

        resp = requests.get(url)
        if not resp.ok:
            return None

        scraper = MangaScraper(sources[source])
        scraper.markup = resp.text
        manga = scraper.manga
        Clock.schedule_once(partial(self.update_info, manga, scraper), 0)

    def update_info(self, manga, scraper, *_):
        self.manga_title = manga.title
        for chapter in manga.chapters:
            self.chapter_list.data.append({"app": self.app, "text": chapter.title, "chapter": chapter, "scraper": scraper})