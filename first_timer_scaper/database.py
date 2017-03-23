import json
import os
import threading
import copy

class Database:

    file_name = None
    def get_initial_data(self):
        return "change the get_initial_data attribute"
    
    def __init__(self):
        self.__data = self.get_initial_data()
        self.__lock = threading.RLock()
        self.__current_thread = None
        self.__folder = None
        assert self.file_name, "Set a file_name in before creating databases."
        
    def save_to(self, folder):
        """Save the credentials to this location."""
        os.makedirs(folder, exist_ok=True)
        self.__folder = folder
        
    def is_persistent(self):
        """Whether the credentials canbe loaded and saved."""
        return self.__folder is not None
        
    @property
    def path(self):
        assert self.is_persistent()
        return os.path.join(self.__folder, self.file_name)
        
    def _load(self):
        """Load the credentials from the disk."""
        assert self.is_persistent()
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.__data = json.load(f)

    def _save(self):
        """Save the credentials."""
        assert self.is_persistent()
        with open(self.path, "w") as f:
            json.dump(self.__data, f)

    def __iter__(self):
        return iter(copy.copy(self.data[:]))
    
    @property
    def data(self):
        assert self.is_owned()
        return self.__data
    
    def is_owned(self):
        return threading.current_thread() is self.__current_thread
        
    def __enter__(self):
        self.__lock.acquire()
        self.__current_thread = threading.current_thread()
        try:
            if self.is_persistent():
                self._load()
        except:
            self.__lock.release()
            raise
        return self
    
    def __exit__(self, error_type, error, traceback):
        try:
            if self.is_persistent() and error_type is None:
                self._save()
        finally:
            self.__current_thread = None
            self.__lock.release()