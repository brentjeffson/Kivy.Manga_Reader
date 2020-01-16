from webscrape2.constants import Source
from webscrape2.scraper import MangaScraper
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, Clock


class SearchPage(BoxLayout):
    search_list = ObjectProperty()
    nav_library_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search(self, keyword, source):
        sources = {
            "Manganelo": Source.MANGANELO,
            "Mangakakalot": Source.MANGAKAKALOT,
            "LeviatanScans": Source.LEVIATANSCANS,
        }
        scraper = MangaScraper(sources[source])
        mangas = scraper.search_online(keyword)
        Clock.schedule_once(partial(self.update_search_list, mangas, source), 1)
    
    def update_search_list(self, mangas, source, *_):
        self.search_list.data = []
        for manga in mangas:
            self.search_list.data.append({"text": manga.title, "manga": manga, "source": source})