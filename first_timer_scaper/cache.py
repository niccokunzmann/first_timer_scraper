from .response import Response
import os

class PathCache:
    """Cache in a folder."""

    def __init__(self, folder):
        self._folder = folder
        self._response_folder = os.path.join(self._folder, "responses")
        self._repo_folder = os.path.join(self._folder, "repositories")
    
    def get_response(self, url):
        """Get a response for the url."""
        return Response.from_path(self._response_folder, url)
    
    def cache_response(self, response):
        """Cache a response."""
        response.to_path(self._response_folder)

    def get_repository(self, full_name):
        """Get a repository for the full name."""
        return Repository.from_path(self._repo_folder, full_name)
    
    def cache_repository(self, repository):
        """Cache a repository."""
        repository.to_path(self._repo_folder)

class NoCache:
    """Not caching."""

    def get_response(self, *args):
        pass
    
    cache_response = get_repository = cache_repository = get_response