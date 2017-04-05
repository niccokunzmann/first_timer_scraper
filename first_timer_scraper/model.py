import time
from .database import Database
import copy
from pprint import pprint

def now():
    """Return the current time in equivalent to github format.
    
    This is Greenwith Mean Time (UTC).
    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
START = now()

class Model(Database):

    # all starting with _ are internal, need a `with self:`
    # all without underscode do not need a `with self:`
    
    file_name = "model.json"
    get_initial_data = dict
    
    def _get_organization(self, organization):
        self.data.setdefault(organization, {})
        return self._get_organization_read_only(organization)
    
    def _get_organization_read_only(self, organization):
        org = self.data.get(organization, {})
        org.setdefault("repos", {})
        org.setdefault("first_timer_prs", {})
        org.setdefault("last_update_requested", START)
        return org
        
    def _get_repository(self, organization, repository_name):
        org = self._get_organization(organization)
        org["repos"].setdefault(repository_name, {})
        return self._get_repository_read_only(organization, repository_name)

    def _get_repository_read_only(self, organization, repository_name):
        org = self._get_organization_read_only(organization)
        repo = org["repos"].get(repository_name, {})
        repo.setdefault("last_update_requested", START)
        repo.setdefault("first_timer_prs", {})
        return repo
        
    def get_repository_read_only(self, organization, repository_name):
        with self:
            return copy.deepcopy(self._get_repository_read_only(organization.lower(), repository_name.lower()))
    
    def get_organization_read_only(self, organization):
        with self:
            return copy.deepcopy(self._get_organization_read_only(organization.lower()))
            
    def get_last_update_of_organization(self, organization):
        with self:
            return self._get_organization_read_only(organization.lower())["last_update_requested"]
            
    def get_last_update_of_repository(self, organization, repository_name):
        with self:
            return self._get_repository_read_only(organization.lower(), repository_name.lower())["last_update_requested"]
            
    def get_pullrequest_read_only(self, organization, repository_name, pr_number):
        organization = organization.lower()
        repository_name = repository_name.lower()
        with self:
            repo = self._get_repository_read_only(organization, repository_name)
            contributor_name = repo["first_timer_prs"][str(pr_number)]
            contributor = self._get_organization_read_only(contributor_name)
            contribution = contributor["first_timer_prs"][organization + "/" + repository_name]
            assert str(contribution["number"]) == str(pr_number), "model inconsistent {}/{}#{}".format(organization, repository_name, pr_number)
            return contribution
            
    def add_first_timer_contribution(self, github_user, repository,
                                     pull_request_number,
                                     pull_request_created_at):
        github_user = github_user.lower()
        repository = repository.lower()
        assert github_user.count("/") == 0
        assert repository.count("/") == 1
        assert isinstance(pull_request_number, int)
        org_name, repo_name = repository.split("/")
        with self:
            first_timer = self._get_organization(github_user)
            if repository in first_timer["first_timer_prs"]:
                if first_timer["first_timer_prs"][repository]["number"] < pull_request_number:
                    # found earlier pull-request
                    return
            first_timer["first_timer_prs"][repository] = {
                "number": pull_request_number,
                "created_at": pull_request_created_at,
                "last_update_requested": now()
            }
            repo = self._get_repository(org_name, repo_name)
            repo["first_timer_prs"][pull_request_number] = github_user
        
    def update_requested(self, entry_name):
        """Log that an update was requested."""
        entry_name = entry_name.lower()
        with self:
            if "/" in entry_name:
                org, repo = entry_name.split("/")
                to_update = self._get_repository(org, repo)
            else:
                to_update = self._get_organization(entry_name)
            to_update["last_update_requested"] = now()
