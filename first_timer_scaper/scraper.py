import os
from concurrent.futures import ThreadPoolExecutor
import threading
from .cache import NoCache
import requests
from .response import Response
import functools

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
        
def unique_step(parallel):
    """Shorten the call for calling a function after the other is completed.
    
        @serial_step
        def get(self, url):
            return parallel thing
        
        @get(url):
        def next_step():
            pass
    
    When the arguments to the function are the same, the call can not be
    done in parallel. It gets executed once and the result is passed two
    both results.
    """
    executor = ThreadPoolExecutor(NUMBER_OF_THREADS)
    lock = threading.Lock()
    requesting = {}
    @functools.wraps(parallel)
    def record_call(*args):
        def call_function_when_done(function):
            with lock:
                future = requesting.get(args)
                if not future:
                    future = self._executor.submit(parallel, *args)
                    requesting[args] = future
                    @future.add_done_callback
                    def end_with_result(self, future):
                        with lock:
                            requesting.pop(args)
            @future.add_done_callback
            def call_with_result(future):
                function(future.result())
    return record_call

class Scraper:

    def __init__(self, credentials):
        self._credentials = credentials
        self._executor = ThreadPoolExecutor(NUMBER_OF_THREADS)
        self._lock = threading.Lock()
        self._cache = NoCache()
        self._requesting_lock = threading.Lock()
        self._requesting = {} # url : future
        
    @unique_step
    def get(self, url):
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
        return result
    
    def set_cache(self, cache):
        self._cache = cache
        
    def start(self):
        pass
                
    def scrape_organization(self, organization):
        """Add all repositories from the organization."""
        print("scrape organization", organization)
        @self.get_each("https://api.github.com/orgs/{}/repos".format(organization))
        def add_repository(repository):
            self.scrape_repository(repository["full_name"])
    
    def get_each(self, url):
        """Request a url"""
        def add_call(function):
            @self.get(url)
            def call_each(result):
                if result.next_page:
                    self.get(result.next_page)(call_each)
                for element in result.json:
                    function(element)
        return add_call
        
    @unique_step
    def clone(self, full_name):
        print("cloning", full_name)
        return 123
    
    def scrape_repository(self, repository):
        print("scrape repository", repository)
        @self.clone(repository)
        def done(v):
            print("done:", v)
            
__all__ = ["Scraper"]
