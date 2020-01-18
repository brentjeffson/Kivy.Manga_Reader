from functools import partial
from os import path
from utils import LAYOUT_DIR

from webscrape2.constants import Source
from webscrape2.scraper import MangaScraper

from pages.infopage import InfoPage
from pages.imagepage import ImagePage
from pages.librarypage import LibraryPage
from pages.searchpage import SearchPage

from kivy.app import App
from kivy.properties import ObjectProperty, Clock, ListProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button

import threading
import requests

print(path.join(LAYOUT_DIR, "library_layout.kv"))
Builder.load_file(path.join(LAYOUT_DIR, "library_layout.kv"))


class ChapterListItem(RecycleDataViewBehavior, Button):

    def on_press(self):
        threading.Thread(target=partial(self.app.image_page.get_image_urls, self.chapter, self.scraper)).start()
        self.app.page("Image")

class ImageList(RecycleView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChapterList(RecycleView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SearchListItem(RecycleDataViewBehavior, Button):
    
    def on_press(self):
        print(f"Opening -> {self.manga.url}")
        threading.Thread(target=partial(app.info_page.get_manga, self.manga.url, self.source), daemon=True).start()
        app.page("Info")


class SearchRecycleView(RecycleView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MangaReaderApp(App):
    navigation_tab = ObjectProperty()

    def build(self):
        self.screen_manager = ScreenManager()

        self.library_page = LibraryPage(app)
        self.search_page = SearchPage()
        self.info_page = InfoPage(self)
        self.image_page = ImagePage(self)
        
        self._create_page(self.screen_manager, self.library_page, "Library")
        self._create_page(self.screen_manager, self.search_page, "Search")
        self._create_page(self.screen_manager, self.info_page, "Info")
        self._create_page(self.screen_manager, self.image_page, "Image")

        self.library_page.nav_search_btn.bind(on_press=partial(self.page, "Search"))
        self.search_page.nav_library_btn.bind(on_press=partial(self.page, "Library"))
        self.info_page.nav_library_btn.bind(on_press=partial(self.page, "Library"))
        self.image_page.nav_library_btn.bind(on_press=partial(self.page, "Library"))
        self.image_page.nav_info_btn.bind(on_press=partial(self.page, "Info"))

        return self.screen_manager
    
    def on_stop(self):
        print("Closing Application...Terminating Threads")
        self.image_page.closing()

    def page(self, page_name, *_):
        self.screen_manager.current = page_name

    @staticmethod
    def _create_page(screen_manager, page, name):
        screen = Screen(name=name)
        screen.add_widget(page)
        screen_manager.add_widget(screen)


if __name__ == "__main__":
    app = MangaReaderApp()
    app.run()