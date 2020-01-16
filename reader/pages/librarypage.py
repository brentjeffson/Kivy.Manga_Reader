from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, ObjectProperty
from functools import partial
import threading


class LibraryPage(BoxLayout):
    sources = ListProperty(["Manganelo", "Mangakakalot", "LeviatanScans"])
    keyword_input = ObjectProperty()

    nav_search_btn = ObjectProperty()

    source = "Manganelo"

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def search(self):
        keyword = self.keyword_input.text
        threading.Thread(target=partial(self.app.search_page.search, keyword, self.source), daemon=True).start()
        self.keyword_input.text = ""

    def on_source_change(self, source):
        self.source = source
