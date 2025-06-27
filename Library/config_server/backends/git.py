import asyncio
import os
import pygit2
import yaml
from pathlib import Path
from .utils import log_error
from concurrent.futures import ThreadPoolExecutor

class GitConfigBackend:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_path = Path("config-repo")
        self.repo = None
        self.current_commit = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    async def connect(self):
        """Clone or update repository with error handling"""
        try:
            if self.repo_path.exists():
                self.repo = pygit2.Repository(str(self.repo_path))
                await self._run_in_executor(self._fetch_updates)
            else:
                self.repo = await self._run_in_executor(
                    pygit2.clone_repository, 
                    self.repo_url, 
                    str(self.repo_path)
                )
            self.current_commit = self.repo.head.target
        except Exception as e:
            log_error(f"Git connection failed: {e}")
            raise

    def _fetch_updates(self):
        """Thread-safe git operations"""
        self.repo.remotes["origin"].fetch()
        self.repo.checkout("origin/main")
        
    async def get_config(self, service: str, env: str) -> Dict[str, Any]:
        """Async config loading"""
        path = self.repo_path / service / f"{env}.yaml"
        content = await self._run_in_executor(self._load_file, path)
        return yaml.safe_load(content)
    
    def _load_file(self, path: Path) -> str:
        with open(path, "r") as f:
            return f.read()
    
    async def watch_changes(self):
        """Efficient change detection"""
        while True:
            await asyncio.sleep(30)
            try:
                await self._run_in_executor(self._fetch_updates)
                if self.repo.head.target != self.current_commit:
                    self.current_commit = self.repo.head.target
                    yield self.current_commit
            except Exception as e:
                log_error(f"Git watch error: {e}")
    
    def get_changed_services(self, commit_id: str) -> List[str]:
        """Detect service-level changes"""
        diff = self.repo.diff(commit_id + "~1", commit_id)
        services = set()
        for delta in diff.deltas:
            if delta.new_file.path:
                parts = delta.new_file.path.split("/")
                if len(parts) > 1: services.add(parts[0])
        return list(services)
    
    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)
