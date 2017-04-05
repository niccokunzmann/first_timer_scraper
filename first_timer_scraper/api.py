from pprint import pprint

class Api:

    def __init__(self, model):
        self._model = model

    def get_organizations(self):
        """Get the data as defined in the API"""
        with self._model:
            orgs = list(self._model.data)
        return {name: self.get_organization(name) for name in orgs}

    def get_organization(self, organization_name):
        """Get the data as defined in the API"""
        m_organization = self._model.get_organization_read_only(organization_name)
        organization = self.get_minimal_organization(organization_name)
        organization["repositories"] = repositories = {}
        organization["first_timers"] = first_timers = {}
        organization["pull_requests_in_organization"] = pull_requests_in_organization = {}
        for m_repository_name, m_repository in m_organization["repos"].items():
            #        "first_timer_prs": {
            #          112: "contributor1"
            #        },
            #        "last_update_requested": "2011-01-26T19:01:12Z"
            repositories[m_repository_name] = self.get_minimal_repository(organization_name, m_repository_name)
            for m_pullrequest_number, m_contributor in m_repository["first_timer_prs"].items():
                if m_contributor not in first_timers:
                    first_timers[m_contributor] = self.get_minimal_user(m_contributor)
                pullrequest = self.get_minimal_pullrequest(organization_name, m_repository_name, m_pullrequest_number)
                pull_requests_in_organization[pullrequest["full_name"]] = pullrequest
        organization["number_of_first_timers"] = len(first_timers)
        organization["number_of_repositories"] = len(repositories)
        organization["number_of_pull_requests_in_organization"] = len(pull_requests_in_organization)
        return organization
    get_user = get_organization

    def get_repository(self, organization_name, repository_name):
        """Get the data as defined in the API"""
        m_repository = self._model.get_repository_read_only(organization_name, repository_name)
        repository = self.get_minimal_repository(organization_name, repository_name)
        repository["owner"] = self.get_minimal_organization(organization_name)
        repository["first_timers"] = first_timers = {}
        repository["first_timer_pull_requests"] = first_timer_pull_requests = {}
        for m_pullrequest_number, m_contributor_name in m_repository["first_timer_prs"].items():
            first_timers[m_contributor_name] = self.get_minimal_user(m_contributor_name)
            pull_request = self.get_minimal_pullrequest(organization_name, repository_name, m_pullrequest_number)
            first_timer_pull_requests[pull_request["full_name"]] = pull_request
        repository["number_of_first_timers"] = len(first_timers)
        repository["number_of_first_timer_pull_requests"] = len(first_timer_pull_requests)
        return repository
        
    def get_minimal_organization(self, name):
        return {"name": name,
                "urls": self.get_organization_urls(name),
                "last_update": self._model.get_last_update_of_organization(name)}

    def get_minimal_user(self, name):
        return {"name": name,
                "urls": self.get_user_urls(name),
                "last_update": self._model.get_last_update_of_organization(name)}
                
    def get_minimal_repository(self, org, repo):
        return {"name": repo,
                "full_name": org + "/" + repo,
                "urls": self.get_repository_urls(org, repo),
                "last_update": self._model.get_last_update_of_repository(org, repo)}

    def get_minimal_pullrequest(self, org, repo, number):
        pr = self._model.get_pullrequest_read_only(org, repo, number)
        return {"name": repo + "#" + str(number),
                "full_name": org + "/" + repo + "#" + str(number),
                "urls": self.get_pullrequest_urls(org, repo, number),
                "number": int(number),
                "repository_full_name": org + "/" + repo,
                "last_update": pr["last_update_requested"],
                "created_at": pr["created_at"]}

    def get_organization_urls(self, name):
        return {
            "html": "/organization/{}.html".format(name),
            "json": "/organization/{}.json".format(name),
            "github_html": "https://github.com/{}".format(name),
            "github_api": "https://api.github.com/orgs/{}".format(name)}

    def get_repository_urls(self, org, repo):
        full_name = org + "/" + repo
        return {
            "html": "/repository/{}.html".format(full_name),
            "json": "/repository/{}.json".format(full_name),
            "github_html": "https://github.com/{}".format(full_name),
            "github_api": "https://api.github.com/repos/{}".format(full_name)}

    def get_user_urls(self, name):
        return {
            "html": "/user/{}.html".format(name),
            "json": "/user/{}.json".format(name),
            "github_html": "https://github.com/{}".format(name),
            "github_api": "https://api.github.com/users/{}".format(name)}

    def get_pullrequest_urls(self, org, repo, number):
        return {
            "html": "https://github.com/{}/{}/pull/{}".format(org, repo, number),
            "json": "https://api.github.com/repos/{}/{}/pulls/{}".format(org, repo, number),
            "github_html": "https://github.com/{}/{}/pull/{}".format(org, repo, number),
            "github_api": "https://api.github.com/repos/{}/{}/pulls/{}".format(org, repo, number)}
