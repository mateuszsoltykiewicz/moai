# config_server/backends/git.py
import asyncio
import pygit2
from os.path import exists
from pyyaml import yaml

class GitConfigBackend:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo = None
        self.current_commit = None
        
    async def connect(self):
        """Clone/pull repository"""
        if exists("config-repo"):
            self.repo = pygit2.Repository("config-repo")
            self.repo.remotes["origin"].fetch()
        else:
            self.repo = pygit2.clone_repository(self.repo_url, "config-repo")
        self.current_commit = self.repo.head.target
    
    def get_config(self, service: str, env: str) -> dict:
        """Load config from repository"""
        path = f"config-repo/{service}/{env}.yaml"
        with open(path, "r") as f:
            return yaml.safe_load(f)
    
    async def watch_changes(self):
        """Monitor repository for changes"""
        while True:
            await asyncio.sleep(30)
            self.repo.remotes["origin"].fetch()
            if self.repo.head.target != self.current_commit:
                yield self.repo.head.target
                self.current_commit = self.repo.head.target
