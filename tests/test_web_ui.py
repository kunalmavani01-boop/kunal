import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from project_360_degree_ai_prompt_assistant_platform.prompt_library import LibraryPrompt
from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings
from project_360_degree_ai_prompt_assistant_platform.web_ui import (
    _build_final_prompt_result,
    _effective_library_category,
    _extract_audience_phrase,
    _fill_template_with_fallbacks,
    _find_template,
    _library_prompt_candidates,
    _merge_prefills,
    _prefill_field,
    _remote_prompt_from_form,
    _render_library_category_options,
    _write_current_launch_url,
)


class WebUiLogicTests(unittest.TestCase):
    def test_audience_extraction_avoids_product_phrases(self) -> None:
        text = "I want to make a website with 3d assets for a job search website better than linkedin"
        value = _extract_audience_phrase(text.lower(), text)
        self.assertEqual(value, "")

    def test_product_strategy_prefill_keeps_subject_specific(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = "I want to make a website with 3d assets for a job search website better than linkedin"
        product = _prefill_field("product", text, template)
        self.assertIn("website", product.lower())
        self.assertNotIn("i want to", product.lower())

    def test_labeled_screen_text_does_not_leak_into_library_prefills(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = (
            "Topic create an AI business where I am building skills connectors different kinds of products "
            "Search intent inform and persuade Tone clear and practical "
            "Call to action produce a clear usable answer"
        )
        values = _merge_prefills(current_values={}, template=template, rough_prompt=text)
        self.assertEqual(values["product"], "an AI business where I am building skills connectors different kinds of products")
        self.assertNotIn("Search intent", values["product"])
        self.assertNotIn("Call to action", " ".join(values.values()))
        self.assertNotIn("action produce", " ".join(values.values()).lower())

    def test_labeled_screen_text_does_not_leak_into_final_prompt_context(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = (
            "Topic create an AI business where I am building skills connectors different kinds of products "
            "Search intent inform and persuade Tone clear and practical "
            "Call to action produce a clear usable answer"
        )
        values = _merge_prefills(current_values={}, template=template, rough_prompt=text)
        result = _build_final_prompt_result(
            rough_prompt=text,
            inspection=None,
            template=template,
            field_values=values,
            extra_notes="",
            avoid_text="",
            lane="library",
        )
        final_prompt = result["final_prompt"]
        self.assertIn("AI business", final_prompt)
        self.assertNotIn("Search intent", final_prompt)
        self.assertNotIn("Call to action", final_prompt)
        self.assertNotIn("action produce", final_prompt.lower())

    def test_ai_business_prompt_does_not_treat_usability_as_audience(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = (
            "create an AI business where I am building skills, connectors, different kinds of products, "
            "and a rack pipeline by collecting all the AI news on a daily basis, and then the agent will "
            "filter out the right ideas by understanding gaps in the market and give me three or four "
            "options which I can start building. I am a non-coder, so this has to be very user-friendly"
        )
        values = _merge_prefills(current_values={}, template=template, rough_prompt=text)
        self.assertIn("AI business", values["product"])
        self.assertNotIn("very user-friendly", values.get("audience", ""))

    def test_browser_capture_text_is_not_used_as_product_subject(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = (
            "These live in Chrome Edge and are one click. GoFullPage Chrome Edge captures the entire "
            "current page as PNG or PDF. Built in Microsoft Edge Web Capture screenshot copied to clipboard."
        )
        values = _merge_prefills(current_values={}, template=template, rough_prompt=text)
        self.assertNotIn("Chrome Edge", values.get("product", ""))
        filled = _fill_template_with_fallbacks(
            template_text=template["prompt_text"],
            field_values=values,
            template=template,
            rough_prompt=text,
        )
        self.assertNotIn("Chrome Edge", filled)
        self.assertIn("the product or service", filled)

    def test_label_words_inside_real_subjects_are_preserved(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        audience_product = _prefill_field("product", "I want to create an audience research platform for founders", template)
        tone_product = _prefill_field("product", "I want to build a tone analysis tool for support teams", template)
        cta_product = _prefill_field("product", "I want to launch a call to action builder for marketers", template)
        self.assertIn("audience research platform", audience_product)
        self.assertIn("tone analysis tool", tone_product)
        self.assertIn("call to action builder", cta_product)

    def test_legitimate_browser_capture_prompt_keeps_subject(self) -> None:
        template = _find_template("product-strategy-brief")
        self.assertIsNotNone(template)
        text = "Help me compare Chrome screenshot capture extensions that export full-page PNG and PDF files"
        product = _prefill_field("product", text, template)
        self.assertIn("Chrome screenshot capture extensions", product)

    def test_remote_prompt_lookup_returns_cached_prompt(self) -> None:
        prompt = LibraryPrompt(
            title="Open Source Prompt",
            pack="General Prompt Repair Pack",
            subcategory="Prompt Repair",
            domain="General",
            interest="General",
            summary="A cached prompt.",
            prompt_text="Act as a senior strategist and rewrite this prompt.",
            source_label="prompts.chat",
            source_url="https://example.com",
            origin="remote",
        )
        assistant = type(
            "AssistantStub",
            (),
            {"library": type("LibraryStub", (), {"cached_remote_prompts": lambda self: [prompt]})()},
        )()
        result = _remote_prompt_from_form(assistant, {"remote_index": "0"})
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Open Source Prompt")

    def test_library_category_options_include_mvp_building(self) -> None:
        html = _render_library_category_options(selected_flow_id="mvp_building")
        self.assertIn("MVP Building", html)
        self.assertIn("value='mvp_building' selected", html)
        self.assertIn("Validation &amp; Research", html)
        self.assertIn("APIs &amp; Architecture", html)

    def test_effective_library_category_prefers_prompt_intent(self) -> None:
        flow_id = _effective_library_category(
            selected_library_category="",
            rough_prompt="I want to validate and scope an MVP for a startup product launch",
            best_match=None,
        )
        self.assertEqual(flow_id, "mvp_building")

    def test_library_prompt_candidates_show_mixed_ranked_options(self) -> None:
        remote_prompt = LibraryPrompt(
            title="Lean MVP Scoping Coach",
            pack="Product Strategy Pack",
            subcategory="Product Strategy",
            domain="Business",
            interest="Founders",
            summary="Scope the first release tightly.",
            prompt_text="Help me define the smallest useful MVP and what to leave out.",
            source_label="awesome-ai-prompts",
            source_url="https://example.com",
            origin="remote",
        )
        local_prompt = LibraryPrompt(
            title="Product Strategy Brief",
            pack="Product Strategy Pack",
            subcategory="Product Strategy",
            domain="Business",
            interest="Founders",
            summary="Turn a startup idea into a tighter MVP scope.",
            prompt_text="Define the user, the core problem, the smallest launch scope, and the key success metric.",
            source_label="Built-in Pack",
            source_url="local",
            origin="local",
            template_fields=["product", "audience", "goal"],
            common_missing_elements=["audience", "goal"],
            repair_hints=["Trim the first release to the smallest useful version."],
            keywords=["mvp", "scope", "startup"],
            why_it_works=["Anchors the prompt to a real user problem."],
        )
        assistant = type(
            "AssistantStub",
            (),
            {
                "library": type(
                    "LibraryStub",
                    (),
                    {
                        "cached_remote_prompts": lambda self: [remote_prompt],
                        "local_prompts": lambda self: [local_prompt],
                    },
                )()
            },
        )()
        cards, total = _library_prompt_candidates(
            assistant=assistant,
            rough_prompt="Help me scope an MVP for a startup idea",
            flow_id="mvp_building",
            best_match={"pack": "Product Strategy Pack", "subcategory": "Product Strategy", "title": "Product Strategy Brief"},
            selected_template_id="",
            limit=8,
        )
        self.assertGreaterEqual(total, 2)
        html = "".join(cards)
        self.assertIn("Product Strategy Brief", html)
        self.assertIn("Lean MVP Scoping Coach", html)
        self.assertIn("Use Prompt", html)
        self.assertIn("Adapt to My Need", html)

    def test_library_prompt_candidates_filters_for_expanded_category(self) -> None:
        remote_prompt = LibraryPrompt(
            title="API Design Reviewer",
            pack="Code Explainer Pack",
            subcategory="APIs",
            domain="Coding",
            interest="Builders",
            summary="Review an API design.",
            prompt_text="Review this API design and suggest endpoint improvements and integration risks.",
            source_label="bundled-open-source",
            source_url="local-seed",
            origin="remote",
        )
        assistant = type(
            "AssistantStub",
            (),
            {
                "library": type(
                    "LibraryStub",
                    (),
                    {
                        "cached_remote_prompts": lambda self: [remote_prompt],
                        "local_prompts": lambda self: [],
                    },
                )()
            },
        )()
        cards, total = _library_prompt_candidates(
            assistant=assistant,
            rough_prompt="Help me review an API design",
            flow_id="apis_architecture",
            best_match=None,
            selected_template_id="",
            limit=10,
        )
        self.assertEqual(total, 1)
        self.assertIn("API Design Reviewer", "".join(cards))

    def test_write_current_launch_url_persists_current_preview_link(self) -> None:
        with TemporaryDirectory() as temp_dir:
            app_home = Path(temp_dir) / ".prompt_assistant"
            settings = AppSettings(
                app_home=app_home,
                db_path=app_home / "memory.sqlite3",
                default_provider="local",
                openai_model="gpt-4.1",
                gemini_model="gemini-3.5-flash",
                memory_limit=3,
            )
            assistant = type("AssistantStub", (), {"settings": settings})()
            _write_current_launch_url(assistant, "http://127.0.0.1:51450/")
            self.assertEqual(
                (app_home / "current_url.txt").read_text(encoding="utf-8"),
                "http://127.0.0.1:51450/",
            )


if __name__ == "__main__":
    unittest.main()
