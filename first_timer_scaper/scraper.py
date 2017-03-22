import os

class Scraper:

    def __init__(self, credentials):
        self._credentials = credentials
    
    def save_to(self, folder):
        os.makedirs(folder, exist_ok=True)
        
    def start(self):
        pass