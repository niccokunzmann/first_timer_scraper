import json
import os
import threading
import copy
import traceback

class Database:

    file_name = None
    def get_initial_data(self):
        return "change the get_initial_data attribute"
    
    def __init__(self):
        self.__data = self.get_initial_data()
        self.__lock = threading.RLock()
        self.__current_thread = []
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
                try:
                    self.__data = json.load(f)
                except ValueError:
                    pass

    def _save(self):
        """Save the credentials."""
        assert self.is_persistent()
        with open(self.path, "w") as f:
            json.dump(self.__data, f, indent=2)

    def __iter__(self):
        with self:
            return iter(list(self.data))
    
    @property
    def data(self):
        assert self.is_owned()
        return self.__data
    
    def is_owned(self):
        return self.__current_thread and threading.current_thread() is self.__current_thread[-1]
        
    def __enter__(self):
        self.__lock.acquire()
        self.__current_thread.append(threading.current_thread())
        try:
            if self.is_persistent() and len(self.__current_thread) == 1:
                self._load()
        except:
            self.__lock.release()
            raise
        return self
    
    def __exit__(self, error_type, error, traceback):
        try:
            if self.is_persistent() and error_type is None and len(self.__current_thread) == 1:
                self._save()
        finally:
            popped = self.__current_thread.pop()
            self.__lock.release()
            assert popped is threading.current_thread(), "inconsistent allocation"