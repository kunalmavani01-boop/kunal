"""Application settings for the local-first prompt assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    app_home: Path
    db_path: Path
    default_provider: str
    openai_model: str
    gemini_model: str
    memory_limit: int

    @classmethod
    def from_env(cls) -> "AppSettings":
        default_home = Path.cwd() / ".prompt_assistant"
        app_home = Path(
            os.getenv(
                "PROMPT_ASSISTANT_HOME",
                str(default_home),
            )
        )
        db_path = Path(
            os.getenv(
                "PROMPT_ASSISTANT_DB",
                str(app_home / "memory.sqlite3"),
            )
        )
        return cls(
            app_home=app_home,
            db_path=db_path,
            default_provider=os.getenv("PROMPT_ASSISTANT_PROVIDER", "local"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            memory_limit=int(os.getenv("PROMPT_ASSISTANT_MEMORY_LIMIT", "3")),
        )

    def ensure_app_home(self) -> None:
        self.app_home.mkdir(parents=True, exist_ok=True)
