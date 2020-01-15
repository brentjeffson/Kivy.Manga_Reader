from pathlib import Path
from os import path

BASE_DIR = path.dirname(__file__)
LAYOUT_DIR = path.join(BASE_DIR, "layouts")

class Layouts:
    
    @staticmethod
    def layout_path(layout):
        return Path(path.join(LAYOUT_DIR, layout))






