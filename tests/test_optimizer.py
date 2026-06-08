import unittest

from project_360_degree_ai_prompt_assistant_platform.optimizer import (
    analyze_prompt,
    build_improved_prompt,
)


class PromptOptimizerTests(unittest.TestCase):
    def test_vague_prompt_gets_actionable_gaps(self) -> None:
        analysis = analyze_prompt("help me")
        self.assertLess(analysis.score, 70)
        self.assertGreaterEqual(len(analysis.gaps), 3)
        self.assertTrue(any("format" in item.lower() for item in analysis.suggestions))
        self.assertTrue(analysis.repair_mode)
        self.assertTrue(analysis.risk_flags)
        self.assertIn("clarity", analysis.subscores)

    def test_improved_prompt_contains_structure_and_memory(self) -> None:
        analysis = analyze_prompt(
            "Write a launch email for a prompt assistant",
            extra_context="Audience is startup founders.",
            output_format="short email",
            constraints=["Keep it under 180 words."],
        )
        improved = build_improved_prompt(
            "Write a launch email for a prompt assistant",
            analysis,
            memories=[
                {
                    "id": 4,
                    "prompt_preview": "Past launch copy focused on ROI and speed.",
                    "feedback": "This angle performed well.",
                }
            ],
            extra_context="Audience is startup founders.",
            output_format="short email",
            constraints=["Keep it under 180 words."],
        )
        self.assertIn("Task:", improved)
        self.assertIn("Context:", improved)
        self.assertIn("Relevant local memory", improved)
        self.assertIn("Output Format:", improved)

    def test_clear_prompt_scores_as_usable_or_better(self) -> None:
        analysis = analyze_prompt(
            "Write a concise launch email for startup founders about a prompt assistant.",
            extra_context="Audience is seed-stage founders comparing AI tools.",
            output_format="short email with subject line",
            constraints=["Keep it under 180 words.", "Avoid hype."],
        )
        self.assertGreaterEqual(analysis.score, 75)
        self.assertIn(analysis.health_label, {"Usable", "Strong"})
        self.assertFalse(analysis.repair_mode)


if __name__ == "__main__":
    unittest.main()
