import os
import subprocess
import tempfile
from collections import namedtuple

def git(*args, **kw):
    try:
        return subprocess.check_output(["git"] + list(args), stderr=subprocess.STDOUT, **kw)
    except subprocess.CalledProcessError as e:
        for line in e.output.split(b"\n"):
            print(line.strip())
        raise

class Repository:
    """This is a repository on the file system."""

    @classmethod
    def from_path(cls, path, full_name):
        org, repo = full_name.split("/")
        full_path = os.path.join(path, org, repo)
        git_path = os.path.join(full_path, ".git")
        if os.path.exists(git_path):
            repo = cls(full_name)
            repo.to_path(full_path)
            return repo
        return None

    def __init__(self, full_name):
        self._folder = tempfile.mkdtemp()
        self._full_name = full_name
        self.to_path(self._folder)
        self._commits = None
        
    @property
    def clone_url(self):
        return "https://github.com/{}.git".format(self._full_name)
    
    @property
    def full_name(self):
        return self._full_name
        
    def git(self, *args, **kw):
        kw.setdefault("cwd", self._folder)
        print("in", self._folder, "git", *args)
        return git(*args,**kw)
    
    @property
    def _git_path(self):
        return os.path.join(self._folder, ".git")
        
    def update(self):
        if os.path.exists(self._git_path):
            self.git("fetch")
            self.git("pull")
        else:
            git("clone", self.clone_url, self._folder)
            
    def to_path(self, base_folder):
        org, repo = self._full_name.split("/")
        folder = os.path.join(base_folder, org, repo)
        os.makedirs(folder, exist_ok=True)
        if folder != self._folder and os.path.exists(self._git_path):
            shutil.move(self._git_path, folder)
        self._folder = folder
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._full_name)
        
    def can_have_first_timers(self):
        return len(self.git("log", "--pretty=format:%ae<%an").splitlines()) > 1
        
    @property
    def pull_requests_url(self):
        return "https://api.github.com/repos/{}/pulls?state=all".format(self._full_name)
    
    
    commit_attributes = ["hash", "author_name", "author_email", "author_date", "subject"]
    @property
    def commits(self):
        """
        %H  Commit hash
            attribute: hash
        %h  Abbreviated commit hash
        %T  Tree hash
        %t  Abbreviated tree hash
        %P  Parent hashes
        %p  Abbreviated parent hashes
        %an Author name
            attribute: author_name
        %ae Author email
            attribute: author_email
        %ad Author date (format respects the --date=option)
            attibute: author_date
        %ar Author date, relative
        %cn Committer name
        %ce Committer email
        %cd Committer date
        %cr Committer date, relative
        %s  Subject
            attribute: subject
        """
        if self._commits == None:
            logs = []
            for format in ["%H", "%an", "%ae", "%ad", "%s"]:
                all_lines = self.git("log", "--pretty=format:" + format)
                try:
                    all_lines = all_lines.decode()
                except UnicodeEncodeError:
                    pass
                all_lines = all_lines.splitlines()
                logs.append(all_lines)
            self._commits = list(map(lambda t: Commit(*t), zip(*logs)))
        return self._commits
    
    def is_first_timer_commit(self, sha):
        mode = 0 # 0 = search for commit
                 # 1 = skip same authors
                 # 2 = skip different authors
                 # 3 = found author again
        for commit in self.commits:
            # prepare input
            if mode in (1, 2):
                is_pr_author = commit.author_email == email or \
                               commit.author_name == name
            # transistion between states
            if mode == 0:
                if commit.hash == sha:
                    mode = 1
                    email = commit.author_email
                    name  = commit.author_name
            elif mode == 1:
                if not is_pr_author:
                    mode = 2
            elif mode == 2:
                if is_pr_author:
                    mode = 3
#        if mode == 0:
#            # closed pull-request
#            print("Could not find commit", sha, "in", self, "for", pr)
        return mode == 2

Commit = namedtuple("Commit", Repository.commit_attributes)