"""
Hook registry for endpoint processing
"""

from typing import Callable, Dict, Any, Optional
import importlib

class HookRegistry:
    _hooks: Dict[str, Callable] = {}
    
    def register(self, name: str, hook: Callable):
        """Register a hook function"""
        self._hooks[name] = hook
        
    def get(self, name: str) -> Optional[Callable]:
        """Get a hook function by name"""
        return self._hooks.get(name)
    
    def load_from_path(self, path: str) -> Callable:
        """Dynamically load a hook function from module path"""
        if path in self._hooks:
            return self._hooks[path]
        
        try:
            module_path, func_name = path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            self.register(path, func)
            return func
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load hook {path}: {str(e)}")

# Global hook registry instance
hook_registry = HookRegistry()
