from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import ObjectProperty, Clock
from kivy.lang import Builder
from functools import partial
import requests
import concurrent.futures
import threading
import io

close_pools = False

class ImagePage(BoxLayout):
    image_recycleview = ObjectProperty()

    nav_library_btn = ObjectProperty()
    nav_info_btn = ObjectProperty()

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def cancel_tasks(self, page_name):
        self.closing()
        self.app.page(page_name)

    def closing(self):
        global close_pools
        close_pools = True

    def get_image_urls(self, chapter, scraper, *_):
        resp = requests.get(chapter.url)
        if not resp.ok:
            return
        image_urls = scraper.get_images(resp.text)
        threading.Thread(target=self.initiate_downloads, args=[image_urls], daemon=True).start()

    def initiate_downloads(self, image_urls, *_):
    
        Clock.schedule_once(partial(self.preload, len(image_urls)), 0)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = [executor.submit(self.download_image, url, index) for index, url in enumerate(image_urls)]

            for future in concurrent.futures.as_completed(results):
                if future.result() is None: break
                image_byte = future.result()[0] 
                filename = future.result()[1]
                index = future.result()[2]
    
                if image_byte is not None:
                    print(f"Image Downloaded -> {filename}")
                    Clock.schedule_once(partial(self.update_images, image_byte, filename, index), 0)

    def download_image(self, image_url, index):
        global close_pools
        if close_pools: 
            print(f"Cancelling Task -> Download({image_url})")
            return None
        print(f"Downloading Image -> {image_url}")
        split_url = image_url.split("/")
        filename = split_url[len(split_url)-1]
        
        resp = requests.get(image_url)
        image_byte = b""
        for chunk in resp.iter_content(chunk_size=1024):
            if close_pools:
                print(f"Closing Task...{image_url}")
                return None
            else: 
                image_byte += chunk
        if close_pools: return None 

        return (image_byte, filename, index) if resp.ok else (None, None, None)
    
    def preload(self, no_image, *_):
        texture = CoreImage("res/loading.png").texture
        for n in range(no_image):
            self.image_recycleview.data.append({"texture": texture, "allow_stretch": True, "size": (600, 800)})

    def update_images(self, image_byte, filename, index, *_):
        split_filename = filename.split(".")
        ext = split_filename[len(split_filename)-1]

        texture = CoreImage(io.BytesIO(image_byte), ext=ext).texture
        self.image_recycleview.data[index] = {
            "texture": texture, 
            "allow_stretch": True, 
            "size": texture.size,
            "size_hint": (None, None)
        }


