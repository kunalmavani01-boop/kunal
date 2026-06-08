import tempfile
import unittest
from pathlib import Path

from project_360_degree_ai_prompt_assistant_platform.prompt_library import (
    PromptLibrary,
    classify_library_flow_ids,
)
from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings


class PromptLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        app_home = Path(self.temp_dir.name)
        self.settings = AppSettings(
            app_home=app_home,
            db_path=app_home / "memory.sqlite3",
            default_provider="local",
            openai_model="gpt-4.1",
            gemini_model="gemini-3.5-flash",
            memory_limit=3,
        )
        self.library = PromptLibrary(self.settings)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_local_search_finds_built_in_prompt(self) -> None:
        results = self.library.search(query="cold outreach email")
        self.assertTrue(any(item.title == "Cold Outreach Email Builder" for item in results))

    def test_filter_lists_include_all_and_known_values(self) -> None:
        categories = self.library.available_categories()
        packs = self.library.available_packs()
        subcategories = self.library.available_subcategories()
        domains = self.library.available_domains()
        interests = self.library.available_interests()
        self.assertIn("All", categories)
        self.assertIn("Writing & Content", categories)
        self.assertIn("All", packs)
        self.assertIn("Blog Outline Pack", packs)
        self.assertIn("All", subcategories)
        self.assertIn("SEO Outlines", subcategories)
        self.assertIn("All", domains)
        self.assertIn("Marketing", domains)
        self.assertIn("All", interests)
        self.assertIn("Outreach", interests)

    def test_pack_filter_returns_matching_prompts(self) -> None:
        results = self.library.search(pack="Proposal Pack")
        self.assertTrue(results)
        self.assertTrue(all(item.pack == "Proposal Pack" for item in results))

    def test_category_filter_returns_matching_prompts(self) -> None:
        results = self.library.search(category="Coding & Technical")
        self.assertTrue(results)
        self.assertTrue(all(self.library.category_for_pack(item.pack) == "Coding & Technical" for item in results))

    def test_prompt_pack_metadata_is_available(self) -> None:
        results = self.library.search(pack="General Prompt Repair Pack")
        self.assertTrue(results)
        self.assertTrue(results[0].common_missing_elements)
        self.assertTrue(results[0].repair_hints)
        self.assertTrue(results[0].template_fields)

    def test_subcategory_filter_returns_matching_prompts(self) -> None:
        results = self.library.search(pack="Study Guide Pack", subcategory="Study Guides")
        self.assertTrue(results)
        self.assertTrue(all(item.subcategory == "Study Guides" for item in results))

    def test_recommend_returns_best_matching_pack(self) -> None:
        recommendations = self.library.recommend("Write a cold outreach email for startup founders")
        self.assertTrue(recommendations)
        self.assertEqual(recommendations[0].pack, "Email Writing Pack")

    def test_recommend_routes_business_idea_to_strategy_pack(self) -> None:
        recommendations = self.library.recommend(
            "I want to build a job search platform with 3D assets and find the right market gap for users"
        )
        self.assertTrue(recommendations)
        self.assertIn(
            recommendations[0].pack,
            {"Product Strategy Pack", "Business Idea Validation Pack"},
        )

    def test_recommend_routes_screenplay_prompt_to_story_pack(self) -> None:
        recommendations = self.library.recommend(
            "Build a screenplay agent for writers and directors that improves scenes and story structure"
        )
        self.assertTrue(recommendations)
        self.assertEqual(recommendations[0].pack, "Story Idea Pack")

    def test_core_packs_have_multiple_built_in_prompts(self) -> None:
        counts = {}
        for item in self.library.local_prompts():
            counts[item.pack] = counts.get(item.pack, 0) + 1
        for pack in [
            "Blog Outline Pack",
            "Email Writing Pack",
            "Product Strategy Pack",
            "Business Idea Validation Pack",
            "Proposal Pack",
            "Meeting Summary Pack",
            "Code Explainer Pack",
            "Bug Fix Pack",
            "Study Guide Pack",
            "Paper Summary Pack",
            "Story Idea Pack",
            "General Prompt Repair Pack",
        ]:
            self.assertGreaterEqual(counts.get(pack, 0), 3, f"{pack} should have at least 3 built-in prompts")

    def test_remote_prompts_include_bundled_seed_entries(self) -> None:
        remote = self.library.cached_remote_prompts()
        titles = {item.title for item in remote}
        self.assertIn("Weekly Planning Coach", titles)
        self.assertIn("Bug Reproduction Assistant", titles)

    def test_remote_prompts_merge_seed_and_cache_without_duplicates(self) -> None:
        self.library.cache_path.write_text(
            """
            [
              {
                "title": "Weekly Planning Coach",
                "prompt_text": "Act as a weekly productivity coach. Reflect on the following input from my past week: {past_week_summary}. Based on that, generate a plan for the coming week, including top 3 goals, habits to track, and key lessons."
              },
              {
                "title": "Custom Remote Prompt",
                "prompt_text": "Help me turn this rough prompt into a final version."
              }
            ]
            """.strip(),
            encoding="utf-8",
        )
        remote = self.library.cached_remote_prompts()
        titles = [item.title for item in remote]
        self.assertEqual(titles.count("Weekly Planning Coach"), 1)
        self.assertIn("Custom Remote Prompt", titles)

    def test_classify_library_flow_ids_routes_prompt_into_specific_buckets(self) -> None:
        flows = classify_library_flow_ids(
            title="MVP Scope Critic",
            prompt_text="Help me trim this product idea into the smallest shippable MVP and explain what to cut.",
            pack="Product Strategy Pack",
            subcategory="MVP Planning",
            domain="Business",
            interest="Founders",
        )
        self.assertIn("mvp_building", flows)
        self.assertIn("product_strategy", flows)

    def test_remote_prompt_taxonomy_is_not_mostly_general_use(self) -> None:
        remote = self.library.cached_remote_prompts()
        general_use_count = 0
        for prompt in remote:
            flows = classify_library_flow_ids(
                title=prompt.title,
                prompt_text=prompt.prompt_text,
                pack=prompt.pack,
                subcategory=prompt.subcategory,
                domain=prompt.domain,
                interest=prompt.interest,
            )
            if flows == {"general_use"}:
                general_use_count += 1
        self.assertLess(general_use_count, len(remote) // 2)


if __name__ == "__main__":
    unittest.main()
