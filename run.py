from utils import Layouts
from kivy.app import App
from kivy.lang import Builder


Builder.load_file(Layouts.layout_path("library_layout.kv"))

class LibraryPage(BoxLayout):

    def __init__(self, *kwargs):
        super().__init__(*kwargs)


class MangaReaderApp(App):

    def build(self):
        self.screen_manager = ScreenManager()

        self.library_page = LibraryPage()
        self._create_page(self.screen_manager, self.library_page, "Library")

        return self.screen_manager

    @staticmethod
    def _create_page(screen_manager, page, name):
        screen = Screen(name)
        screen.add_widget(page)
        screen_manager.add_widget(screen)


if __name__ == "__main__":
    app = MangaReaderApp()
    app.run()