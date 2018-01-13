import time

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def to_string(t):
    """Return the time in equivalent to github format.
    
    This is Greenwich Mean Time (GMT).
    """
    return time.strftime(FORMAT, time.gmtime(t))


def now():
    return to_string(time.time())
    

START = to_string(0)

def is_older_than_seconds(string_time, seconds):
    return string_time < to_string(time.time() - seconds)

    
