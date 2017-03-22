import sys
import tempfile
import shutil
import os
from pprint import pprint
from bottle import run, get, static_file, request, response, post, redirect
from . import service

APPLICATION = 'first_timer_scraper'
ZIP_PATH = "/" + APPLICATION + ".zip"
HERE = os.path.dirname(__file__)
STATIC_FILES = os.path.join(HERE, "static")

def static(file):
    return redirect("/static/" + file)

def todo():
    raise NotImplementedError("This is still under construction.")

@get("/static/<path:path>")
def get_static_file(path):
    return static_file(path, root=STATIC_FILES)

@post("/organization/<organization>")
def add_organization(organization):
    """Submit an organization for scraping.
    This shows an html page with a link to the status of the organization.
    """
    todo()

@get("/organizations.<ending>")
def get_all_organizations(ending):
    """List all organizations with links to their statuses."""
    todo()

@get("/organization/<organization>.<ending>")
def get_organization(organization, repository, ending):
    """Get an organization and its status.
    """
    todo()

@get("/repositories.<ending>")
def get_all_repositories(ending):
    """List all organizations with links to their statuses."""
    todo()

@post("/repository/<organization>/<repository>")
def add_repository(organization, repository):
    """Sumbit a repository for scraping
    This shows an html page with a link to the status of the repository.
    """
    todo()

@get("/repository/<organization>/<repository>.<ending>")
def get_repository(organization, repository, ending):
    """Get the repository and its status.  
    """
    todo()

@post("/auth")
def add_user():
    """Add `username` and `password` to those usable to scrape github.
    
    They will be tried and removed if invalid.
    """
    return static("auth-added.html")

@get("/auth")
def get_user_form():
    """Show a form to register a new authentication.
    """
    return static("add-github-authentication.html")

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

@get('/source')
def get_source_redirect():
    """Get the source code as a zip file."""
    redirect(ZIP_PATH)

@get(ZIP_PATH)
def get_source():
    """Download the source of this application."""
    # from http://stackoverflow.com/questions/458436/adding-folders-to-a-zip-file-using-python#6511788
    directory = tempfile.mkdtemp()
    temp_path = os.path.join(directory, APPLICATION)
    zip_path = shutil.make_archive(temp_path, "zip", HERE)
    pprint(locals())
    return static_file(APPLICATION + ".zip", root=directory)

def main():
    #service.DATA_FOLDER = sys.argv[1]
    #service.SECRETS_FOLDER = sys.argv[2]
    #service.run()
    run(host="", port=8080, debug=True)

if __name__ == "__main__":
    main()
