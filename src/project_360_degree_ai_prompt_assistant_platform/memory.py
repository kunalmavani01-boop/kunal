"""Local SQLite memory store for prompts and feedback."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from project_360_degree_ai_prompt_assistant_platform.optimizer import tokenize


@dataclass
class MemoryEntry:
    id: int
    created_at: str
    prompt: str
    improved_prompt: str
    feedback: str
    rating: int | None
    analysis: dict
    tags: list[str]

    def to_preview(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "prompt_preview": compact(self.prompt),
            "improved_preview": compact(self.improved_prompt),
            "feedback": self.feedback,
            "rating": self.rating,
            "analysis": self.analysis,
        }


class PromptMemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    improved_prompt TEXT NOT NULL,
                    feedback TEXT NOT NULL DEFAULT '',
                    rating INTEGER,
                    analysis_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL DEFAULT '[]'
                )
                """
            )
            connection.commit()

    def add_entry(
        self,
        prompt: str,
        improved_prompt: str,
        analysis: dict,
        tags: Iterable[str] | None = None,
    ) -> int:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload = (
            created_at,
            prompt,
            improved_prompt,
            json.dumps(analysis),
            json.dumps([tag for tag in (tags or []) if tag]),
        )
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO prompt_memory (
                    created_at,
                    prompt,
                    improved_prompt,
                    analysis_json,
                    tags_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                payload,
            )
            connection.commit()
            return int(cursor.lastrowid)

    def add_feedback(self, entry_id: int, feedback: str, rating: int | None = None) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE prompt_memory
                SET feedback = ?, rating = ?
                WHERE id = ?
                """,
                (feedback, rating, entry_id),
            )
            connection.commit()

    def recent(self, limit: int = 10) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, prompt, improved_prompt, feedback, rating, analysis_json, tags_json
                FROM prompt_memory
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_entry(row).to_preview() for row in rows]

    def recent_full(self, limit: int = 20) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, prompt, improved_prompt, feedback, rating, analysis_json, tags_json
                FROM prompt_memory
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_entry(row).__dict__ for row in rows]

    def similar(self, prompt: str, limit: int = 3) -> list[dict]:
        query_tokens = set(tokenize(prompt))
        if not query_tokens:
            return []

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, prompt, improved_prompt, feedback, rating, analysis_json, tags_json
                FROM prompt_memory
                ORDER BY id DESC
                LIMIT 100
                """
            ).fetchall()

        scored: list[tuple[float, MemoryEntry]] = []
        for row in rows:
            entry = self._row_to_entry(row)
            candidate_tokens = set(tokenize(entry.prompt + " " + entry.improved_prompt))
            overlap = len(query_tokens & candidate_tokens)
            if not overlap:
                continue
            union = len(query_tokens | candidate_tokens)
            base_score = overlap / union if union else 0.0
            rating_boost = (entry.rating or 0) * 0.02
            scored.append((base_score + rating_boost, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry.to_preview() for _, entry in scored[:limit]]

    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=int(row["id"]),
            created_at=str(row["created_at"]),
            prompt=str(row["prompt"]),
            improved_prompt=str(row["improved_prompt"]),
            feedback=str(row["feedback"] or ""),
            rating=int(row["rating"]) if row["rating"] is not None else None,
            analysis=json.loads(row["analysis_json"]),
            tags=json.loads(row["tags_json"]),
        )


def compact(text: str, limit: int = 90) -> str:
    single_line = " ".join(text.split())
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3].rstrip() + "..."
