import unittest

from project_360_degree_ai_prompt_assistant_platform.guided import (
    GuidedPromptBlueprint,
    build_guided_prompt,
    suggest_prompt_upgrades,
)
from project_360_degree_ai_prompt_assistant_platform.optimizer import analyze_prompt


class GuidedPromptTests(unittest.TestCase):
    def test_guided_prompt_contains_expected_sections(self) -> None:
        blueprint = GuidedPromptBlueprint(
            task="write a landing page for my prompt assistant",
            goal="the page convinces founders to book a demo",
            context_files=["brief.md - brand voice and audience"],
            reference_text="Reference page with a strong hero section and proof points.",
            reference_patterns=["use a sharp headline", "show concrete proof quickly"],
            output_type="landing page copy",
            recipient="startup founders",
            desired_action="book a demo",
            avoid="generic AI buzzwords",
            success_criteria="the page feels premium and conversion-focused",
            rules=["Keep it concise.", "Avoid jargon-heavy claims."],
        )
        prompt = build_guided_prompt(blueprint)
        self.assertIn("Task:", prompt)
        self.assertIn("Context Files:", prompt)
        self.assertIn("Reference:", prompt)
        self.assertIn("Success Brief:", prompt)
        self.assertIn("Rules:", prompt)
        self.assertIn("Plan:", prompt)

    def test_guided_prompt_scores_higher_than_raw_task(self) -> None:
        raw = analyze_prompt("write a landing page")
        blueprint = GuidedPromptBlueprint(
            task="write a landing page",
            goal="it gets founders interested in the assistant",
            output_type="landing page",
            recipient="startup founders",
            desired_action="request a demo",
            success_criteria="the message feels clear and premium",
            rules=["Keep the copy direct."],
        )
        structured = analyze_prompt(build_guided_prompt(blueprint), output_format="landing page", constraints=["Keep the copy direct."])
        self.assertGreater(structured.score, raw.score)

    def test_short_prompt_gets_smart_upgrade_ideas(self) -> None:
        ideas = suggest_prompt_upgrades("write a landing page")
        self.assertGreaterEqual(len(ideas), 3)
        self.assertTrue(any("audience" in item.lower() for item in ideas))
        self.assertTrue(any("format" in item.lower() or "length" in item.lower() for item in ideas))


if __name__ == "__main__":
    unittest.main()
