import os
import subprocess
import tempfile

def git(*args, **kw):
    try:
        return subprocess.check_output(["git"] + list(args), stderr=subprocess.STDOUT, **kw)
    except subprocess.CalledProcessError as e:
        for line in e.output.split(b"\n"):
            print(line.strip())
        raise

class Repository:

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
        
    @property
    def clone_url(self):
        return "https://github.com/{}.git".format(self._full_name)
    
    @property
    def full_name(self):
        return self._full_name
        
    def git(self, *args, **kw):
        kw.setdefault("cwd", self._folder)
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
            
    def to_path(self, folder):
        os.makedirs(folder, exist_ok=True)
        org, repo = self._full_name.split("/")
        folder = os.path.join(folder, org, repo)
        if folder != self._folder and os.path.exists(self._git_path):
            shutil.move(self._git_path, folder)
        self._folder = folder
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._full_name)
        