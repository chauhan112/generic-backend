from handlers import IHandler, HandlerWrapper
import os
from rlib.useful.SearchSystem import FilesContentSearch
from git import Repo
import shutil
import stat
from rlib.useful.Path import Path as PathTools


BASE_DIR = "./.cloned_repos"
os.makedirs(BASE_DIR, exist_ok=True)

class Tools:
    @staticmethod
    def repo_name(repo_url: str) -> str:
        return repo_url.rstrip("/").split("/")[-1]
    @staticmethod
    def repo_name_without_extension(repo_url: str) -> str:
        name = Tools.repo_name(repo_url)
        if name.endswith(".git"):
            name = name[:-4]
        return name

class GitHubHandlerClone(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/github/clone"
    def validate_params(self, params: dict):
        required_fields = ["repo"]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")
        
        if params.get("is_private", False):
            if "token" not in params:
                 raise ValueError("Private repositories require a 'token' field.")
        return True
    
    def call_handler(self, params: dict):
        repo_url = params["repo"]
        is_private = params.get("is_private", False)
        token = params.get("token")
        if is_private and token:
            if repo_url.startswith("https://"):
                repo_url = repo_url.replace("https://", f"https://{token}@", 1)
            else:
                # Handle cases where URL might not start with https:// or use other protocols if needed
                pass

        repo_name = Tools.repo_name_without_extension(repo_url)
        os.makedirs(BASE_DIR, exist_ok=True)
        destination_path = os.path.join(BASE_DIR, repo_name)

        if os.path.exists(destination_path):
            return {"message": f"Repository already exists at {destination_path}", "path": destination_path}

        try:
            Repo.clone_from(repo_url, destination_path)
            return {"message": f"Successfully cloned {repo_name}", "path": destination_path}
        except Exception as e:
            error_msg = str(e).replace(token, "***") if token else str(e)
            return {"error": f"Failed to clone repository: {error_msg}"}

class GitHubHandlerPull(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/github/pull"
    def validate_params(self, params: dict):
        required_fields = ["repo"]
        str_fields = {"repo": "str", "branch": "str(optional)"}
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field} expected type: {str_fields[field]}")
        return True
    def call_handler(self, params: dict):
        repo_path = params["repo"]
        branch = params.get("branch", "main")
        name = Tools.repo_name_without_extension(repo_path)
        repo_path = os.path.join(BASE_DIR, name)
        repo = Repo(repo_path)
        repo.git.pull()
        return {"message": f"Successfully pulled {branch} from {repo_path}"}

class GitHubHandlerListRepos(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/github/list_repos"
    def validate_params(self, params: dict):
        return True
    def call_handler(self, params: dict):
        """return [{"repo_url": "", "local_path": ""}]"""
        repos = []
        for repo_name in os.listdir(BASE_DIR):
            repo_path = os.path.join(BASE_DIR, repo_name)
            if os.path.isdir(repo_path):
                repo = Repo(repo_path)
                origin_url = repo.remotes.origin.url
                repos.append({"repo_url": origin_url, "local_path": repo_name})
        return repos

class GitHubHandlerGetFileContent(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/github/get_file_content"
    def validate_params(self, params: dict):
        required_fields = ["repo", "file"]
        str_fields = {"repo": "str", "file": "str"}
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field} expected type: {str_fields[field]}")
        return True
    def call_handler(self, params: dict):
        repo_path = params["repo"]
        name = Tools.repo_name_without_extension(repo_path)
        file_path = os.path.join(BASE_DIR, name, params["file"])
        with open(file_path, "r") as file:
            return {"content": file.read()}

class GitHubHandlerSearch(IHandler):
    def __init__(self):
        self.search_system = FilesContentSearch([])
    def is_current_path(self, path: str) -> bool:
        return path == "/github/search"
    def validate_params(self, params: dict):
        required_fields = ["repo"]
        str_fields = {"repo": "str", "extension": "[str](optional)", "word": "str(optional)", "case": "bool(optional)", "reg": "bool(optional)"}
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field} expected type: {str_fields[field]}")
        return True
    def call_handler(self, params: dict):
        """{"files": [{"name":"file1.txt", "line":1}, {"name":"file2.txt", "line":2,}]}"""
        repo_path = params["repo"]
        name = Tools.repo_name_without_extension(repo_path)
        repo_path = os.path.join(BASE_DIR, name)
        extensions = params.get("extensions", [])
        word = params.get("word", "")
        case = params.get("case", False)
        reg = params.get("reg", False)
        files = list(PathTools.find_files(repo_path, extensions, ignore_folders=[".git"]))
        self.search_system.set_file_paths(files)
        results = self.search_system.search(word, case, reg)
        return [{"name": self.file_path_relative_to_repo(repo_path, file), "line": line} for file, line in results]

    def file_path_relative_to_repo(self, repo_path: str, file_path: str) -> str:
        return file_path[len(repo_path)+1:]

class GitHubHandlerClean(IHandler):
    def is_current_path(self, path: str) -> bool:
        return path == "/github/clean"
    def validate_params(self, params: dict):
        return True
    def on_rm_error(self, func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    def call_handler(self, params: dict):
        
        if os.path.exists(BASE_DIR):
            for repo in os.listdir(BASE_DIR):
                repo_path = os.path.join(BASE_DIR, repo)
                if os.path.isdir(repo_path):
                    shutil.rmtree(repo_path, onerror=self.on_rm_error)
        return {"message": "Cleaned all repositories"}

class MainGitHubHandler:
    def get_handler():
        handler = HandlerWrapper()
        handler.add_handler(GitHubHandlerClone())
        handler.add_handler(GitHubHandlerSearch())
        handler.add_handler(GitHubHandlerClean())
        handler.add_handler(GitHubHandlerGetFileContent())
        handler.add_handler(GitHubHandlerListRepos())
        handler.add_handler(GitHubHandlerPull())
        return handler
