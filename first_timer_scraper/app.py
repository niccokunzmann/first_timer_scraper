#!/usr/bin/python3
import sys
import json
import tempfile
import shutil
import os
from pprint import pprint
from bottle import run, get, static_file, request, response, post, redirect, SimpleTemplate
from .credentials import Credentials, check_login
from .scraper import Scraper
from .cache import PathCache
from .model import Model
from .api import Api

APPLICATION = 'first_timer_scraper'
ZIP_PATH = "/" + APPLICATION + ".zip"
HERE = os.path.dirname(__file__)
STATIC_FILES = os.path.join(HERE, "static")
TEMPLATE_FOLDER = os.path.join(HERE, "templates")

credentials = Credentials()
model = Model()
credentials.add(None) # scrape github slowly without authentication
scraper = Scraper(credentials, model)
api = Api(model)

def static(file):
    return redirect("/static/" + file)

def template(name, **kw):
    # http://bottlepy.org/docs/dev/stpl.html
    path = os.path.join(TEMPLATE_FOLDER, name)
    with open(path) as f:
        template = SimpleTemplate(f.read())
    return template.render(api=api, **kw)

def badge(number):
    
    if number < 10:
        return template("First Timers-1-blue.svg", number=number)
    if number < 100:
        return template("First Timers-10-blue.svg", number=number)
    return template("First Timers-100-blue.svg", number=number)

def todo():
    raise NotImplementedError("This is still under construction.")

@get("/static/<path:path>")
def get_static_file(path):
    return static_file(path, root=STATIC_FILES)

@post("/organization.<ending>")
def add_organization_html(ending):
    """Submit an organization for scraping.
    This shows an html page with a link to the status of the organization.
    """
    organization = request.forms.get('organization')
    scraper.scrape_organization(organization)
    if ending == "json":
        return {"status": "ok", "urls": api.get_organization_urls(organization)}
    return template("added-organization.html", organization=organization)

@get("/organizations.<ending>")
def get_all_organizations(ending):
    """List all organizations with links to their statuses."""
    if ending == "json":
        response.content_type='application/json'
        return api.get_organizations()
    return template("organizations.html")

@get("/organization/<organization>.<ending>")
def get_organization(organization, ending):
    """Get an organization and its status.
    """
    if ending == "json":
        response.content_type='application/json'
        return api.get_organization(organization)
    if ending == "svg":
        data = api.get_organization(organization)
        return badge(data["number_of_first_timers"])
    return template("organization.html", organization=organization)

@get("/repositories.<ending>")
def get_all_repositories(ending):
    """List all organizations with links to their statuses."""
    todo()

@post("/repository.<ending>")
def add_repository(ending):
    """Sumbit a repository for scraping
    This shows an html page with a link to the status of the repository.
    """
    repository = request.forms.get('repository')
    organization_name, repository_name = repository.split("/")
    scraper.scrape_repository(repository)
    if ending == "json":
        return {"status": "ok", "urls": api.get_repository_urls(organization_name, repository_name)}
    return template("added-repository.html", repository=repository)

@get("/repository/<organization>/<repository>.<ending>")
def get_repository(organization, repository, ending):
    """Get the repository and its status.  
    """
    if ending == "json":
        return api.get_repository(organization, repository)
    return template("repository.html", organization=organization, repository=repository)

@post("/auth")
def add_authentication():
    """Add `username` and `password` to those usable to scrape github.
    
    They will be tried and removed if invalid.
    """
    # http://bottlepy.org/docs/dev/tutorial.html#http-request-methods
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login((username, password)):
        credentials.add((username, password))
        return static("add-github-authentication-success.html")
    return static("add-github-authentication-failure.html")

@get("/auth")
def get_authentication_form():
    """Show a form to register a new authentication.
    """
    return static("add-github-authentication.html")

@post("/user/<user>")
def add_user(user):
    """Trace back the user's repositories to their origins.
    
    Submit all found organizations.
    """
    redirect("/organization/" + user)

@get("/user/<user>.<ending>")
def get_user(user, ending):
    """Return the status of this github user.

    - what are the first-timer repositories?
    """
    redirect("/organization/" + user + "." + ending)

@get("/user.<ending>")
def get_all_users(ending):
    """All the users and their statuses."""
    redirect("/organizations." + ending)

@get("/")
def overview_page():
    """Show a description of the project.

    - Link to this repository#readme.
    - Link to download the code /source.
    - How to contribute.
    - What this is about.
    """
    return static("index.html")

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
    return static_file(APPLICATION + ".zip", root=directory)

def main():
    scraper.set_cache(PathCache(sys.argv[1]))
    credentials.save_to(sys.argv[2])
    model.save_to(sys.argv[3])
    scraper.start()
    run(host="", port=8080, debug=True)

if __name__ == "__main__":
    main()
