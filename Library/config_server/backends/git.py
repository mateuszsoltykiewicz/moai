import asyncio
import os
import pygit2
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from Library.logging import get_logger

logger = get_logger(__name__)

class GitConfigBackend:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_path = Path("config-repo")
        self.repo = None
        self.current_commit = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    async def connect(self):
        try:
            if self.repo_path.exists():
                self.repo = pygit2.Repository(str(self.repo_path))
                await self._run_in_executor(self._fetch_updates)
                logger.info(f"Connected to existing Git repo at {self.repo_path}")
            else:
                self.repo = await self._run_in_executor(
                    pygit2.clone_repository, 
                    self.repo_url, 
                    str(self.repo_path)
                )
                logger.info(f"Cloned Git repo from {self.repo_url} to {self.repo_path}")
            self.current_commit = self.repo.head.target
        except Exception as e:
            logger.error(f"Git connection failed: {e}", exc_info=True)
            raise

    def _fetch_updates(self):
        self.repo.remotes["origin"].fetch()
        self.repo.checkout("origin/main")
        logger.debug("Fetched latest Git changes")
        
    async def get_config(self, service: str, env: str) -> Dict[str, Any]:
        path = self.repo_path / service / f"{env}.yaml"
        content = await self._run_in_executor(self._load_file, path)
        return yaml.safe_load(content)
    
    def _load_file(self, path: Path) -> str:
        with open(path, "r") as f:
            return f.read()
    
    async def watch_changes(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self._run_in_executor(self._fetch_updates)
                if self.repo.head.target != self.current_commit:
                    self.current_commit = self.repo.head.target
                    logger.info(f"Detected Git config change at commit {self.current_commit}")
                    yield self.current_commit
            except Exception as e:
                logger.error(f"Git watch error: {e}", exc_info=True)
    
    def get_changed_services(self, commit_id: str) -> List[str]:
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
