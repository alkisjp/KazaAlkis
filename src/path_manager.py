"""Central path configuration for KazaALKIS runtime resources."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class PathManager:
    """Resolve project-local data and external AI workspace paths."""

    def __init__(self, ai_root: str = None):
        self.ai_root = Path(ai_root or os.getenv("AI_ROOT", r"E:\AI"))
        self.models = Path(os.getenv("AI_MODELS", str(self.ai_root / "models")))
        self.cache = Path(os.getenv("AI_CACHE", str(self.ai_root / "cache")))
        self.outputs = Path(os.getenv("AI_OUTPUTS", str(self.ai_root / "outputs")))
        self.venvs = Path(os.getenv("AI_VENVS", str(self.ai_root / "venvs")))
        self.logs = Path(os.getenv("AI_LOGS", str(self.ai_root / "logs")))
        self.tmp = Path(os.getenv("AI_TMP", str(self.ai_root / "tmp")))
        self.vectorstore = Path(os.getenv("AI_VECTORSTORE", str(self.ai_root / "vectorstore")))
        self.projects = Path(os.getenv("AI_PROJECTS", str(self.ai_root / "projects")))
        self.shared = Path(os.getenv("AI_SHARED", str(self.ai_root / "shared")))
        self.tools = Path(os.getenv("AI_TOOLS", str(self.ai_root / "tools")))

    def ensure_runtime_dirs(self):
        """Create the standard AI workspace directories."""
        for path in self.runtime_dirs().values():
            path.mkdir(parents=True, exist_ok=True)

    def runtime_dirs(self):
        """Return the managed external runtime directories."""
        return {
            "models": self.models,
            "cache": self.cache,
            "outputs": self.outputs,
            "venvs": self.venvs,
            "logs": self.logs,
            "tmp": self.tmp,
            "vectorstore": self.vectorstore,
            "projects": self.projects,
            "shared": self.shared,
            "tools": self.tools,
        }

    @property
    def app_output_dir(self):
        return self.outputs / "KazaALKIS"

    @property
    def app_log_dir(self):
        return self.logs / "KazaALKIS"

    @property
    def app_tmp_dir(self):
        return self.tmp / "KazaALKIS"


def get_paths():
    """Return the active path manager."""
    return PathManager()
