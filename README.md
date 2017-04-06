first_timer_scraper
===================

[![](https://dockerbuildbadges.quelltext.eu/status.svg?repository=first_timer_scraper&organization=niccokunzmann)](https://hub.docker.com/r/niccokunzmann/first_timer_scraper/builds/)
[![](https://firsttimers.quelltext.eu/repository/niccokunzmann/first_timer_scraper.svg)](https://firsttimers.quelltext.eu/repository/niccokunzmann/first_timer_scraper.html)

[Visit the daily build][online].

This is inspired by `first-timers-only` issues:
How can we make it possible for new-comers to contribute to a project.

This web service tries to solve this by looking at the data:

- What is it that first-timers contributed to?
- Did they continue to contribute?
- Which issues did they solve?
- Which projects do best at welcoming new contributors?

First Timer Contributions
-------------------------

To find first timer pull-requests, we look at organizations and
their repositories.

- **What are first timer repositories?**  
  - They MUST have at least two people contributing
  - They MUST have pull requests

- **What is a first-timer pull-request?**
  - They MUST have at least one commmit
  - In the repository history:
    - The issue commit MUST be preceded by commits of the author
    - At least one "other author" MUST have contributed before
    - There MUST NOT be a commit of the author before the "other author"
  - They may be on any branch.

- **What is a first-timer issue?**  
  There is no automatic linking between the pull-request and the issue.
  Thus, we must assume that one of the following takes place:
  - There is a public web page linked in the pull-request.  
    This is the case with external issue trackers like with django.
    We may assume certain issue trackers.
  - The issue is referenced as github issue in the pull-request.
  - The issue is referenced by commits by the author preceding the merge commit.

Implementation
--------------

For each organization sumbitted:
1. submit all repositories

For each submitted repository
1. clone
2. check if it can be a first-timer repository
3. extract for all commits
   - author email
   - author name
   - commit hash
   - time
4. Get all pull-requests
   - Get the first commit
   - Get the author, email
   - Get the github user issuing this pull-request
5. find first-timer pull-requests

API
---

`ENDING` is either `.html` or `.json`.

- General
  - `GET /`  
    Show a description of the project.
    - Link to this repository#readme.
    - Link to download the code /source.
    - How to contribute.
    - What this is about.
  - `GET /source`  
    Get the source code as a zip file.
- Github Authentication:
  - `GET /auth`
    Show a form to register a new authentication.
  - `POST /auth`  
    Add `username` and `password` to those usable to scrape github.
    They will be tried and removed if invalid.
- Organization
  - `GET /organizations<ENDING>`  
    [schema][organizations-schema]
    [example responses][organizations-examples]  
    List all organizations with links to their statuses.    
    Users may be listed among them.
  - `GET /organization/<organization><ENDING>`  
    [schema][organization-schema]
    [example responses][organization-examples]  
    Get an organization and its status.
    Same as the element of `/organizations.json`
    Ending:
    - `json`
    - `html`
    - `svg` ![](https://img.shields.io/badge/First%20Timers-1-blue.svg)
  - `POST /organization<ENDING>`  
    Submit an `organization` for scraping.
    This shows an html page with a link to the status of the organization.
- Repository
  - `GET /repositories<ENDING>`  
    [schema][repositories-schema]
    [example responses][repositories-examples]  
    List all repositories with links to their statuses.
    See below for the content of the list.
  - `GET /repository/<organization>/<repository><ENDING>`  
    [schema][repository-schema]
    [example responses][repository-examples]  
    Get the repository and its status.  
    Ending:
    - `json`
    - `html`
    - `svg` ![](https://img.shields.io/badge/First%20Timers-1-blue.svg)
  - `POST /repository`  
    Sumbit a `repository` for scraping
- User
  - `GET /users<ENDING>`  
    Same as `GET /organizations<ENDING>`.
  - `GET /user/<user><ENDING>`  
    Same as `GET /organization/<user><ENDING>`.
  - `POST /user/<user>`  
    Trace back the user's repositories to their origins.
    Submit all found organizations.
- Issues
  - TODO: do we need an issue endpoint?

[organizations-schema]: first_timer_scaper/tests/schemas/organizations.json
[organizations-examples]: first_timer_scaper/tests/tests/organizations/works
[organization-schema]: first_timer_scaper/tests/schemas/organization.json
[organization-examples]: first_timer_scaper/tests/tests/organization/works
[repositories-schema]: first_timer_scaper/tests/schemas/repositories.json
[repositories-examples]: first_timer_scaper/tests/tests/repositories/works
[repository-schema]: first_timer_scaper/tests/schemas/repository.json
[repository-examples]: first_timer_scaper/tests/tests/repository/works


### Minimal definitions

When objects are defined, they contain minimal definitions.
They can be used to infer the most important data and find the full data.
E.g. `repository["urls"]["json"]` always points to the repository endpoint.

`repository`, `user`, `organization` and `issue` have this in common:
```
{
  "name": "<name>",
  "urls": {
    "html": "<html_url>",
    "json": "<json_url>",
    "github_html": "<github_html_url>",
    "github_api": "<github_json_url>",
  },
  "last_update": "<start_time>",
  }
}
```
- `last_update_time` times are given like this:
  `2011-01-26T19:01:12Z` in UTC.
  You can parse it with
  `time.strptime("2011-01-26T19:01:12Z", "%Y-%m-%dT%H:%M:%SZ")`


- Additionally `repository`, `issue` always define
  ```
  {
    "full_name": "<full_name>"
  }
  ```

Command Line
------------

`python3 -m first_timer_scraper <CACHE_FOLDER> <SECRETS_FOLDER> <MODEL_FOLDER>`

- `CACHE_FOLDER` is the folder where the scraped data is stored.
  This is the cache. It is totally ok to remove all this data.
- `SECRETS_FOLDER` is the folder where the secrets are stored.
  These are the secrets to access thegithub API.
- `MODEL_FOLDER` is the storage place of the model/the data base this is built.
  If you delete this, you can start scraping anew.
  
### Installation

You need to install [Python 3](https://www.python.org/downloads/) and pip.
Under Ubuntu, you can do this:

    sudo apt-get -y install python3 python3-pip

To install all required packages, execute

    pip3 install --user -r requiremets.txt

### Windows

    py -3 -m pip install --user -r requirements.txt
    py -3 -m first_timer_scaper.app data secret model

### Docker

This runs the docker container:

    docker run --rm                                \
               -p 8080:8080                        \
               -v "secret:/app/secret"             \
               -v "model:/app/model"               \
               niccokunzmann/first_timer_scraper

The parameters have the following meaning:
- The API of the first-timer-scraper is available as <http://localhost:8080>.
- The secret data including passwords are stored in the folder `./secret`.
- The model data is stored in the folder `./model`
- `--rm` is for development purposes.
  It removes the container and all the cache when the container stops.

When you ran the command, you can visit <http://localhost:8080>,
submit credentails and scrape repositories.

You can build the Docker image like this:

    docker build . -t niccokunzmann/first_timer_scraper

Data Model
----------

The data model describes what is saved when scraped.

```
{
  "loklak": {
    "repos": {
      "loklak_server": {
        "first_timer_prs": {
          "112": "contributor1"
        },
        "last_update_requested": "2011-01-26T19:01:12Z"
      }
    },
    "last_update_requested": "2011-01-26T19:01:12Z",
    "first_timer_prs":{}
  },
  "contributor1": {
    "first_timer_prs": {
      "loklak/loklak_server": {
        "created_at" : "2011-01-26T19:01:12Z"
        "number": 112 // lowest number wins
        "last_update_requested": "2011-01-26T19:01:12Z"
      }
    },
    "last_update_requested": "2011-01-26T19:01:12Z",
    "repos": {}
  }
}
```

Further Reading
---------------

- Github API:
  - Rate Limiting: https://developer.github.com/v3/#rate-limiting
- PyGithub: https://github.com/PyGithub/PyGithub/

[online]: https://firsttimers.quelltext.eu
