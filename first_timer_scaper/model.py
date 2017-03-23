import time
from .database import Database

def now(self):
    """Return the current time in equivalent to github format.
    
    This is Greenwith Mean Time (UTC).
    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
START = now()

class Model(Database):
    
    file_name = "model.json"
    get_inital_data = dict
    
    def _prepare_organization(self, organization):
        self.data.setdefault(organization, {})
        org = self.data[organization]
        org.setdefault("repos", {})
        org.setdefault("first_timer_prs", {})
        org.setdefault("last_update_requested", START)
        return org
        
    def _prepare_repository(self, organization, repository_name):
        org = self._prepare_organization(organization)
        org["repos"].setdefault(repository_name, {})
        repo = org["repos"][repository_name]
        repo.setdefault("last_update_requested", START)
        repo.setdefault("first_timer_prs", {})
    
    def add_first_timer_contribution(self, github_user, repository,
                                     pull_request_number,
                                     pull_request_created_at):
        assert github_user.count("/") == 0
        assert repository.count("/") == 1
        assert insinstance(pull_request_number, int)
        org_name, repo_name = repository.split("/")
        with self:
            first_timer = self._prepare_organization(github_user)
            repo = self._prepare_repository(org_name, repo_name)
            if repository in first_timer["first_timer_prs"]:
                if first_timer["first_timer_prs"][repository][number] < pull_request_number:
                    # found earlier pull-request
                    return
            first_timer["first_timer_prs"][repository] = {
                "number": pull_request_number,
                "created_at": pull_request_created_at
            }
            repo["first_timer_prs"][pull_request_number] = github_user
        
    def update_requested(self, entry_name):
        """Log that an update was requested."""
        with self:
            if "/" in entry_name:
                org, repo = entry_name.split("/")
                to_update = self._prepare_repository(org, repo)
            else:
                to_update = self._prepare_organization(entry_name)
            to_update["last_update_requested"] = now()
                