
    
def get_org_urls(name):
    return {
        "html": "/organization/{}.html".format(name),
        "json": "/organization/{}.json".format(name),
        "github_html": "https://github.com/{}".format(name),
        "github_api": "https://api.github.com/orgs/{}".format(name)}

def get_repo_urls(full_name):
    return {
        "html": "/repository/{}.html".format(full_name),
        "json": "/repository/{}.json".format(full_name),
        "github_html": "https://github.com/{}".format(full_name),
        "github_api": "https://api.github.com/repos/{}".format(full_name)}

def get_user_urls(name):
    return {
        "html": "/user/{}.html".format(name),
        "json": "/user/{}.json".format(name),
        "github_html": "https://github.com/{}".format(name),
        "github_api": "https://api.github.com/users/{}".format(name)}

def get_pull_urls(org, repo, number):
    return {
        "github_html": "https://github.com/{}/{}/pull/{}".format(org, repo, number),
        "github_api": "https://api.github.com/repos/{}/{}/pulls/{}".format(org, repo, number)}

class Api:

    def __init__(self, model):
        self._model = model

    def get_organizations(self):
        with self:
            return {name: self.get_organization(name)
                    for name in self.data}
    
    def get_organization(self, org_name):
        org = self._model.get_organization_read_only(org_name)
        result = {}
        result["name"] = org_name
        result["repositories"] = repos = {}
        result["first_timers"] = first_timers = []
        for repo_name, _repo in org["repos"].items():
            #        "first_timer_prs": {
            #          112: "contributor1"
            #        },
            #        "last_update_requested": "2011-01-26T19:01:12Z"
            full_name = org_name + "/" + repo_name
            repos[name] = {"name": name,
                           "full_name": full_name,
                           "urls": self.get_repo_urls(full_name)}
            for pr_number, contributor in _repo["first_timer_prs"].items():
                if contributor not in first_timers:
                    first_timers[contributor] = {
                        "name": contributor,
                        "url": self.get_user_urls(contributor),
                        "pull_requests_in_organization": {}
                    }
                prs = first_timers["contributor"]["pull_requests_in_organization"]
                pr_full_name = "{}#{}".format(full_name, pr_number)
                _contributor = self._model.get_organization_read_only(contributor)
                _pr = _contributor["first_timer_prs"][full_name]
                assert _pr["number"] == pr_number, "inconsistent in {}".format(pr_full_name)
                prs[pr_full_name] = {
                    "repository_name": repo_name,
                    "full_name": pr_full_name,
                    "number": pr_number,
                    "created_at": _pr["created_at"],
                    "urls": self.get_pull_urls(org_name, repo_name, pr_number)
                }
        result["urls"] = self.get_org_urls(org_name)
        result["last_update"] = org["last_update_requested"]
        result["number_of_first_timers"] = len(first_timers)
        return result

    def get_org_urls(self, name):
        return {
            "html": "/organization/{}.html".format(name),
            "json": "/organization/{}.json".format(name),
            "github_html": "https://github.com/{}".format(name),
            "github_api": "https://api.github.com/orgs/{}".format(name)}

    def get_repo_urls(self, full_name):
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

    def get_pull_urls(self, org, repo, number):
        return {
            "github_html": "https://github.com/{}/{}/pull/{}".format(org, repo, number),
            "github_api": "https://api.github.com/repos/{}/{}/pulls/{}".format(org, repo, number)}
