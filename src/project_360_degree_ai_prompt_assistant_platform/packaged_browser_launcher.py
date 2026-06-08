"""Release entrypoint for packaged browser beta builds."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from project_360_degree_ai_prompt_assistant_platform.assistant import PromptAssistant
from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings
from project_360_degree_ai_prompt_assistant_platform.web_ui import run_browser_app


def _configure_packaged_app_home() -> None:
    """Make packaged releases use their own bundled app data folder."""

    if not getattr(sys, "frozen", False):
        return

    base_dir = Path(sys.executable).resolve().parent
    app_home = base_dir / ".prompt_assistant"
    os.environ.setdefault("PROMPT_ASSISTANT_HOME", str(app_home))
    os.environ.setdefault("PROMPT_ASSISTANT_DB", str(app_home / "memory.sqlite3"))


def _write_launcher_error(exc: BaseException) -> None:
    app_home = Path(os.getenv("PROMPT_ASSISTANT_HOME", str(Path.cwd() / ".prompt_assistant")))
    app_home.mkdir(parents=True, exist_ok=True)
    log_path = app_home / "launcher-error.log"
    log_path.write_text("".join(traceback.format_exception(exc)), encoding="utf-8")


def main() -> int:
    """Launch the browser beta directly for packaged releases."""

    try:
        _configure_packaged_app_home()
        assistant = PromptAssistant(AppSettings.from_env())
        run_browser_app(assistant)
        return 0
    except Exception as exc:  # pragma: no cover - packaged runtime path
        _write_launcher_error(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
