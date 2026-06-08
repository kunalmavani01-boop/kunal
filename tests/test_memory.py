import gc
import shutil
import tempfile
import unittest
from pathlib import Path

from project_360_degree_ai_prompt_assistant_platform.memory import PromptMemoryStore


class PromptMemoryStoreTests(unittest.TestCase):
    def test_recent_and_similar_entries(self) -> None:
        tmpdir = tempfile.mkdtemp()
        try:
            store = PromptMemoryStore(Path(tmpdir) / "memory.sqlite3")
            entry_id = store.add_entry(
                prompt="Write a product launch email for an AI startup",
                improved_prompt="Task:\nWrite a product launch email for an AI startup",
                analysis={"score": 72},
                tags=["email", "startup"],
            )
            store.add_feedback(entry_id, "Good structure", rating=4)

            recent = store.recent(limit=5)
            similar = store.similar("Create an email for an AI startup launch", limit=3)

            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["id"], entry_id)
            self.assertEqual(recent[0]["rating"], 4)
            self.assertEqual(len(similar), 1)
            self.assertEqual(similar[0]["id"], entry_id)
        finally:
            del store
            gc.collect()
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
