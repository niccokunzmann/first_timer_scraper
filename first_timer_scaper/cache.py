from .response import Response
import os

class PathCache:
    """Cache in a folder."""

    def __init__(self, folder):
        self._folder = folder
    
    def get(self, url):
        """Get a response for the url."""
        return Response.from_path(self._folder, url)
    
    def cache(self, response):
        """Cache a response."""
        response.to_path(self._folder)

class NoCache:
    """Not caching."""

    def get(self, url):
        return None
    
    def cache(self, response):
        pass