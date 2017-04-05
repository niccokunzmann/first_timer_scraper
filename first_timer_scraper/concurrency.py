import functools
import threading
from concurrent.futures import ThreadPoolExecutor
import traceback

NUMBER_OF_THREADS = 100

def unique_step(parallel, numer_of_threads=NUMBER_OF_THREADS):
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
    
    `next_step` will get executed in parallel to where it was defined in all cases.
    """
    executor = ThreadPoolExecutor(numer_of_threads)
    lock = threading.RLock()
    requesting = {}
    @functools.wraps(parallel)
    def record_call(*args):
        def call_function_when_done(function):
            assert callable(function), "{} must be callable. In {}".format(function, parallel)
            with lock:
                future = requesting.get(args)
                if not future:
                    future = executor.submit(parallel, *args)
                    requesting[args] = future
                    @future.add_done_callback
                    def end_with_result(future):
                        with lock:
                            requesting.pop(args)
            @future.add_done_callback
            def call_with_result(future):
                def call_function():
                    try:
                        function(future.result())
                    except:
                        traceback.print_exc()
                executor.submit(call_function)
            return function
        return call_function_when_done
    return record_call
