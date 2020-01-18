from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty, ObjectProperty
from functools import partial
from utils import Library, LIBRARY_PATH, TITLE
from webscrape2.constants import Source
import threading


class LibraryPage(BoxLayout):
    sources = ListProperty(["Manganelo", "Mangakakalot", "LeviatanScans"])
    keyword_input = ObjectProperty()
    nav_search_btn = ObjectProperty()
    library_list = ObjectProperty()

    source = "Manganelo"
    sources = {
        "Manganelo": Source.MANGANELO,
        "Mangakakalot": Source.MANGAKAKALOT,
        "LeviatanScans": Source.LEVIATANSCANS,
    }

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        library = Library.load(LIBRARY_PATH)
        for url in library:
            manga_info = library[url]
            self.library_list.add_widget(Button(text=manga_info[TITLE], on_press=partial(self._open, url)))

    def search_page(self):
        keyword = self.keyword_input.text
        source = self.sources[self.source]
        threading.Thread(target=partial(self.app.search_page.search, keyword, source), daemon=True).start()
        self.keyword_input.text = ""

    def on_source_change(self, source):
        self.source = source

    def _open(self, manga_url, _):
        source = ""
        for key, val in self.sources.items():
            if key.lower() in manga_url:
                source = val
                break
        if source == "": return
        threading.Thread(target=partial(self.app.info_page.get_manga, manga_url, source), daemon=True).start()
        self.app.page("Info")
