import sys
import service
from bottle import run, get, static_file, request, response

def todo():
    raise NotImplementedError("This is still under construction.")

@post("/repository/<organization>")
def add_repository(organization):
    """Submit an organization for scraping.
    This shows an html page with a link to the status of the organization.
    """
    todo()

@get("/organizations.<ending>")
def get_all_users(ending):
    """List all organizations with links to their statuses."""
    todo()

@get("/repository/<organization>.<ending>")
def get_user(organization, repository, ending):
    """Get an organization and its status.
    """
    todo()

@get("/repositories.<ending>")
def get_all_users(ending):
    """List all organizations with links to their statuses."""
    todo()

@post("/repository/<organization>/<repository>")
def add_repository(organization, repository):
    """Sumbit a repository for scraping
    This shows an html page with a link to the status of the repository.
    """
    todo()

@get("/repository/<organization>/<repository>.<ending>")
def get_user(organization, repository, ending):
    """Get the repository and its status.  
    """
    todo()

@post("/auth")
def add_user(user):
    """Add `username` and `password` to those usable to scrape github.
    
    They will be tried and removed if invalid.
    """
    todo()

@post("/user/<user>")
def add_user(user):
    """Trace back the user's repositories to their origins.
    
    Submit all found organizations.
    """
    todo()

@get("/user/<user>.<ending>")
def get_user(user, ending):
    """Return the status of this github user.

    - what are the first-timer repositories?
    """
    todo()

@get("/user.<ending>")
def get_all_users(ending):
    """All the users and their statuses."""
    todo()

@get("/")
def overview_page():
    """Show a description of the project.

    - Link to this repository#readme.
    - Link to download the code /source.
    - How to contribute.
    - What this is about.
    """
    todo()
  
@get("/source")
def get_source():
    """Get the source code as a zip file."""
    todo()

def main():
    service.DATA_FOLDER = sys.argv[1]
    service.SECRETS_FOLDER = sys.argv[2]
    service.run()
    run()

if __name__ == "__main__":
    


