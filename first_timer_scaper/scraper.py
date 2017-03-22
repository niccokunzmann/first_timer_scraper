import os
from concurrent.futures import ThreadPoolExecutor
import threading
from .cache import NoCache
import requests
from .response import Response

NUMBER_OF_THREADS = 100
WAIT_FOR_RETRY_IN_SECONDS = 60

_print = print
PRINT_LOCK = threading.RLock() # use an rlock if something goes wrong with recursion
def print(*args, **kw):
    with PRINT_LOCK:
        return _print(*args, **kw)
        
def secure_auth_print(auth):
    if auth is None:
        return None
    if isinstance(auth, tuple):
        return auth[0]
    else:
        return "<??>"

class Scraper:

    def __init__(self, credentials):
        self._credentials = credentials
        self._executor = ThreadPoolExecutor(NUMBER_OF_THREADS)
        self._lock = threading.Lock()
        self._cache = NoCache()
        self._requesting_lock = threading.Lock()
        self._requesting = {} # url : future
        
    def _get(self, url):
        """Return a Response for the URL or None"""
        with self._lock:
            result = self._cache.get(url)
            if result:
                print("cached", url)
                return result
        # Set User-Agent header
        #   https://developer.github.com/v3/#user-agent-required
        headers = {"User-Agent" : "niccokunzmann/first_timer_scraper"}
        ok = False
        while not ok:
            for auth in self._credentials:
                print("GET", url, "as", secure_auth_print(auth))
                response = requests.get(url, headers=headers, auth=auth)
                rate_limit = response.headers.get("X-RateLimit-Remaining")
                if response.ok:
                    ok = True
                    break
                elif response.status_code == 403 and rate_limit == 0:
                    with self._lock:
                        print("GET", url, "used up", secure_auth_print(auth))
                        self._credentials.used_up(auth)
                else:
                    print("GET", url, "ERROR:", response.status_code, response.reason)
                    response.raise_for_status()
            if not ok:
                time.sleep(WAIT_FOR_RETRY_IN_SECONDS)
                print("GET", url, "waiting")
        print("GET", url, "calls left:", rate_limit)
        result = Response.from_response(response)
        # first cache, then remove the future
        with self._lock:
            self._cache.cache(result)
        with self._requesting_lock:
            self._requesting.pop(url)
        return result
    
    def set_cache(self, cache):
        self._cache = cache
        
    def start(self):
        pass
                
    def scrape_organization(self, organization):
        """Add all repositories from the organization."""
        print("scrape organization", organization)
        @self.each("https://api.github.com/orgs/{}/repos".format(organization))
        def add_repository(repository):
            self.scrape_repository(repository["full_name"])
    
    def each(self, url):
        """Request a url"""
        def add_call(function):
            @self.get(url)
            def call_each(result):
                if result.next_page:
                    self.get(result.next_page)(call_each)
                for element in result.json:
                    function(element)
        return add_call
        
    def get(self, url):
        def add_call(function):
            with self._requesting_lock:
                future = self._requesting.get(url)
                if not future:
                    future = self._executor.submit(self._get, url)
                    self._requesting[url] = future
            @future.add_done_callback
            def call_with_result(future):
                function(future.result())
        return add_call
    
    def scrape_repository(self, repository):
        print("scrape repository", repository)
            
__all__ = ["Scraper"]
