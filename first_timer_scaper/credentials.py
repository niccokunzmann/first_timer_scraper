import requests
import json
import os

class Credentials:

    file_name = "github-authentication.json"
    
    def __init__(self):
        """Credentials for authentication.
        
        Use it like this:
        
            credentials = Credentials()
            credentials.add(None) # no authentication
            for auth in credentials:
                try_authenticate(auth)
            """
        self._auth = []
        self._folder = None
        
    def save_to(self, folder):
        """Save the credentials to this location."""
        os.makedirs(folder, exist_ok=True)
        self._folder = folder
        
    def is_persistent(self):
        """Whether the credentials canbe loaded and saved."""
        return self._folder is not None
        
    @property
    def path(self):
        assert self.is_persistent()
        return os.path.join(self._folder, self.file_name)
        
    def load(self):
        """Load the credentials from the disk."""
        assert self.is_persistent()
        if os.path.exists(self.path):
            with open(self.path) as f:
                self._auth = json.load(f)

    def save(self):
        """Save the credentials."""
        assert self.is_persistent()
        with open(self.path, "w") as f:
            self._auth = json.dump(self._auth, f)

    def __iter__(self):
        return iter(self._auth[:])
        
    def add(self, credentials):
        """Add credentials."""
        with self:
            self._add(credentials)

    def invalid(self, credentials):
        """Remove the credentials."""
        with self:
            self._remove(credentials)
    
    def _add(self, credentials):
        self._auth.append(credentials)
    
    def _remove(self, credentials):
        credentials = (credentials)
        while credentials in self._auth:
            self._auth.remove(credentials)
       
    def used_up(self, credentials):
        """Move the authentication to the end of the line."""
        with self:
            self._remove(credentials)
            self._add(credentials)

    def __enter__(self):
        if self.is_persistent():
            self.load()
        return self
    
    def __exit__(self, error_type, error, traceback):
        if self.is_persistent() and error_type is None:
            self.save()
            
def check_login(credentials):
    """Check if the user and password can authenticate with Github."""
    response = requests.get("https://api.github.com/", auth=credentials)
    return response.ok

__all__ = ["Credentials", "check_login"]