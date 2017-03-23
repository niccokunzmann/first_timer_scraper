import requests
from .database import Database

class Credentials(Database):
    """Credentials for authentication.
    
    Use it like this:
    
        credentials = Credentials()
        credentials.add(None) # no authentication
        for auth in credentials:
            try_authenticate(auth)
        """

    file_name = "github-authentication.json"
    get_initial_data = list
        
    def add(self, credentials):
        """Add credentials."""
        with self:
            self._add(credentials)

    def invalid(self, credentials):
        """Remove the credentials."""
        with self:
            self._remove(credentials)
    
    def _add(self, credentials):
        self.data.append(credentials)
    
    def _remove(self, credentials):
        credentials = (credentials)
        while credentials in self.data:
            self.data.remove(credentials)
       
    def used_up(self, credentials):
        """Move the authentication to the end of the line."""
        with self:
            self._remove(credentials)
            self._add(credentials)


def check_login(credentials):
    """Check if the user and password can authenticate with Github."""
    response = requests.get("https://api.github.com/", auth=credentials)
    return response.ok

__all__ = ["Credentials", "check_login"]