from webscrape2.scraper import MangaScraper
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, Clock

cancel_search = False
class SearchPage(BoxLayout):
    search_list = ObjectProperty()
    nav_library_btn = ObjectProperty()

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.nav_library_btn.bind(on_press=partial(self.page, "Library"))

    def search(self, keyword, source):
        cancel_search = True
        self.search_list.data = []
        
        scraper = MangaScraper(source)
        mangas = scraper.search_online(keyword)
        Clock.schedule_once(partial(self.update_search_list, mangas, source), 1)
    
    def update_search_list(self, mangas, source, *_):
        global cancel_search
        if not cancel_search:
            self.search_list.data = []
            for manga in mangas:
                self.search_list.data.append({"text": manga.title, "manga": manga, "source": source})

    def page(self, page_name):
        self.cancel_search()
        self.app.page(page_name)

    def cancel_search(self):
        global cancel_search
        cancel_search = True