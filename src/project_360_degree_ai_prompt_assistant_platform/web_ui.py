"""Local browser UI for the simplified beta experience."""

from __future__ import annotations

import html
import os
import re
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socket import socket
from typing import Any
from urllib.parse import parse_qs

from project_360_degree_ai_prompt_assistant_platform.pack_catalog import PACK_CATALOG
from project_360_degree_ai_prompt_assistant_platform.prompt_library import (
    LibraryPrompt,
    classify_library_flow_ids,
)


FIELD_LABELS = {
    "agreed_points": "Agreed points",
    "audience": "Audience",
    "call_goal": "Call goal",
    "character_type": "Character type",
    "client_name": "Client name",
    "client_type": "Client type",
    "code_goal": "What the code is trying to do",
    "comparison_goal": "Comparison goal",
    "components": "Key components",
    "concept": "Concept",
    "conflict": "Conflict",
    "constraints": "Constraints",
    "core_opinion": "Core opinion",
    "cta": "Call to action",
    "deliverables": "Deliverables",
    "desired_action": "Desired action",
    "done_definition": "Done definition",
    "ending_type": "Ending type",
    "environment": "Environment",
    "exam_date": "Exam date",
    "example_type": "Example type",
    "expected_behavior": "Expected behavior",
    "expected_outcome": "Expected outcome",
    "flaw": "Main flaw",
    "focus_area": "Focus area",
    "follow_up": "Follow-up needed",
    "format": "Output format",
    "goal": "What a strong answer should achieve",
    "initiative": "Initiative",
    "key_topics": "Key topics",
    "language": "Language",
    "level": "Learner level",
    "main_benefit": "Main benefit",
    "main_risk": "Main risk",
    "main_takeaway": "Main takeaway",
    "meeting_goal": "Meeting goal",
    "offer": "Offer",
    "pain_point": "Pain point",
    "paper_set": "Paper set",
    "paper_topic": "Paper topic",
    "premise": "Premise",
    "pricing_model": "Pricing model",
    "product": "Product or service",
    "proof": "Proof or credibility signal",
    "proof_points": "Proof points",
    "protagonist": "Protagonist",
    "recipient_role": "Recipient role",
    "repro_steps": "Reproduction steps",
    "research_gap": "Research gap",
    "risky_area": "Risky area",
    "scene_goal": "Scene goal",
    "search_intent": "Search intent",
    "service": "Service",
    "setting": "Setting",
    "sources": "Sources",
    "stakeholders": "Stakeholders",
    "stakes": "Stakes",
    "stack": "Tech stack",
    "symptom": "Symptom",
    "system_area": "System area",
    "system_goal": "System goal",
    "task": "Task",
    "team_name": "Team name",
    "test_focus": "Test focus",
    "themes": "Themes",
    "time_available": "Time available",
    "timeframe": "Timeframe",
    "timeline": "Timeline",
    "tone": "Tone",
    "topic": "Topic",
    "topics": "Topics",
    "update_scope": "Update scope",
    "value_case": "Value case",
    "weak_areas": "Weak areas",
}

FIELD_PLACEHOLDERS = {
    "audience": "Example: startup founders, recruiters, junior developers",
    "client_type": "Example: SaaS founder, design agency, school administrator",
    "constraints": "Example: keep it concise, avoid jargon, under 300 words",
    "cta": "Example: book a call, reply with feedback, approve the plan",
    "deliverables": "Example: homepage wireframe, copy deck, launch checklist",
    "format": "Example: bullets, email, table, proposal, step-by-step plan",
    "goal": "Example: help them understand the offer and take the next step",
    "main_benefit": "Example: reduces onboarding time by 40%",
    "pain_point": "Example: low reply rates, unclear positioning, slow execution",
    "proof": "Example: worked with 12 clients, 3x faster workflow, case study link",
    "recipient_role": "Example: recruiter, CTO, marketing lead",
    "service": "Example: website redesign, SEO strategy, AI workflow setup",
    "stakes": "Example: they may lose funding, miss the launch, lose trust",
    "tone": "Example: confident, warm, executive, practical",
    "topic": "Example: AI landing pages, exam prep, debugging a checkout bug",
}

MULTILINE_FIELDS = {
    "agreed_points",
    "components",
    "constraints",
    "deliverables",
    "key_topics",
    "pain_point",
    "paper_set",
    "proof_points",
    "repro_steps",
    "sources",
    "themes",
    "topics",
}

DEFAULT_TEMPLATE_ID = "general-repair-basic"

PROMPT_ARCHETYPES = {
    "logical_text": {
        "label": "Logical / Text Framework",
        "best_for": "Text generation, copywriting, strategy, and general reasoning.",
    },
    "operator_brief": {
        "label": "Role-Task-Instruction-Data",
        "best_for": "Execution prompts where the model needs clear direction and specific inputs.",
    },
    "deep_reasoning": {
        "label": "Deep Reasoning Structure",
        "best_for": "Higher-stakes prompts that need context, success criteria, and stronger rules.",
    },
    "analyst_brief": {
        "label": "Evidence-Led Analyst Brief",
        "best_for": "Research, analysis, industry overviews, and lower-hallucination outputs.",
    },
    "visual_director": {
        "label": "Visual / Cinematic Director",
        "best_for": "Image, video, storyboard, and cinematic generation prompts.",
    },
}

LIBRARY_FLOWS = [
    {
        "id": "mvp_building",
        "label": "MVP Building",
        "description": "Turn an idea into a tighter MVP, scope, and first release plan.",
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack"},
        "keywords": {"mvp", "scope", "launch", "validate", "market", "feature", "startup", "product"},
    },
    {
        "id": "product_strategy",
        "label": "Product Strategy",
        "description": "Sharpen audience, problem, positioning, and feature priorities.",
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack", "Proposal Pack"},
        "keywords": {"product", "positioning", "audience", "strategy", "roadmap", "differentiator"},
    },
    {
        "id": "validation_research",
        "label": "Validation & Research",
        "description": "Find prompts for discovery, interviews, research briefs, and market validation.",
        "packs": {"Business Idea Validation Pack", "Paper Summary Pack", "Meeting Summary Pack"},
        "keywords": {"validate", "research", "interview", "market gap", "evidence", "persona"},
    },
    {
        "id": "website_landing_pages",
        "label": "Website & Landing Pages",
        "description": "Find prompts for landing pages, website structure, and messaging.",
        "packs": {"Blog Outline Pack", "Product Strategy Pack", "Proposal Pack"},
        "keywords": {"website", "landing page", "headline", "copy", "cta", "messaging"},
    },
    {
        "id": "messaging_positioning",
        "label": "Messaging & Positioning",
        "description": "Use prompts for value props, differentiators, headlines, and angles.",
        "packs": {"Product Strategy Pack", "Blog Outline Pack", "Proposal Pack"},
        "keywords": {"messaging", "positioning", "value proposition", "angle", "headline", "differentiator"},
    },
    {
        "id": "sales_outreach",
        "label": "Sales & Outreach",
        "description": "Use proven prompts for emails, follow-ups, and concise communication.",
        "packs": {"Email Writing Pack", "Proposal Pack", "Meeting Summary Pack"},
        "keywords": {"email", "outreach", "sales", "follow-up", "proposal", "reply"},
    },
    {
        "id": "proposals_client_work",
        "label": "Proposals & Client Work",
        "description": "Choose prompts for proposals, scoping, pricing, and client delivery.",
        "packs": {"Proposal Pack", "Meeting Summary Pack"},
        "keywords": {"proposal", "client", "scope", "pricing", "deliverables", "statement of work"},
    },
    {
        "id": "content_seo",
        "label": "Content & SEO",
        "description": "Use prompts for articles, SEO outlines, thought leadership, and content briefs.",
        "packs": {"Blog Outline Pack"},
        "keywords": {"content", "seo", "blog", "article", "outline", "keyword"},
    },
    {
        "id": "social_creator",
        "label": "Social Media & Creator",
        "description": "Use prompts for posts, threads, hooks, creator ideas, and repurposing.",
        "packs": {"Blog Outline Pack", "Email Writing Pack", "General Prompt Repair Pack"},
        "keywords": {"social", "creator", "thread", "linkedin", "twitter", "youtube"},
    },
    {
        "id": "study_learning",
        "label": "Study & Learning",
        "description": "Use prompts for study guides, teaching, and fast learning support.",
        "packs": {"Study Guide Pack", "Paper Summary Pack", "General Prompt Repair Pack"},
        "keywords": {"study", "learn", "teacher", "student", "exam", "revision"},
    },
    {
        "id": "research_summaries",
        "label": "Research Summaries",
        "description": "Use prompts for plain-language summaries, research briefs, and findings.",
        "packs": {"Paper Summary Pack", "Study Guide Pack"},
        "keywords": {"research summary", "paper", "abstract", "findings", "literature"},
    },
    {
        "id": "coding_help",
        "label": "Coding Help",
        "description": "Choose prompts for code explanation, walkthroughs, and technical guidance.",
        "packs": {"Code Explainer Pack"},
        "keywords": {"code", "developer", "function", "programming", "terminal", "explain code"},
    },
    {
        "id": "debugging_fixes",
        "label": "Debugging & Fixes",
        "description": "Use prompts for root cause analysis, bug reproduction, and safe fixes.",
        "packs": {"Bug Fix Pack", "Code Explainer Pack"},
        "keywords": {"debug", "bug", "error", "traceback", "fix", "reproduce"},
    },
    {
        "id": "apis_architecture",
        "label": "APIs & Architecture",
        "description": "Use prompts for API design, integrations, system planning, and architecture.",
        "packs": {"Code Explainer Pack", "Bug Fix Pack"},
        "keywords": {"api", "architecture", "system design", "database", "integration"},
    },
    {
        "id": "story_screenplay",
        "label": "Story & Screenplay",
        "description": "Find prompts for narrative structure, scripts, and story development.",
        "packs": {"Story Idea Pack", "General Prompt Repair Pack"},
        "keywords": {"story", "screenplay", "script", "plot", "writer", "director"},
    },
    {
        "id": "character_scene",
        "label": "Character & Scene Writing",
        "description": "Use prompts for scenes, characters, dialogue, and dramatic beats.",
        "packs": {"Story Idea Pack"},
        "keywords": {"character", "scene", "dialogue", "protagonist", "scene beat"},
    },
    {
        "id": "productivity_planning",
        "label": "Productivity & Planning",
        "description": "Use prompts for weekly planning, priorities, habits, and personal systems.",
        "packs": {"Meeting Summary Pack", "General Prompt Repair Pack"},
        "keywords": {"planning", "weekly", "productivity", "priorities", "habit", "calendar"},
    },
    {
        "id": "decision_making",
        "label": "Decision Making",
        "description": "Use prompts for comparisons, trade-offs, and decision-ready thinking.",
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack", "Meeting Summary Pack"},
        "keywords": {"decision", "trade-off", "comparison", "choose", "pros and cons"},
    },
    {
        "id": "prompt_repair",
        "label": "Prompt Repair",
        "description": "Use broad prompts that rewrite, improve, or sharpen rough requests.",
        "packs": {"General Prompt Repair Pack"},
        "keywords": {"rewrite", "improve", "prompt", "clarify", "refine"},
    },
    {
        "id": "general_use",
        "label": "General Use",
        "description": "Use versatile prompts when you want a fast starting point without overthinking the lane.",
        "packs": {"General Prompt Repair Pack", "Meeting Summary Pack"},
        "keywords": {"general", "assistant", "help me", "starter", "useful"},
    },
]


def run_browser_app(assistant) -> None:
    """Serve the local browser beta and open it for the user."""

    handler = _build_handler(assistant)
    preferred_port = int(os.getenv("PROMPT_ASSISTANT_PORT", "51360"))
    port = _find_open_port(preferred=preferred_port)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}/"
    _write_current_launch_url(assistant, url)

    print(f"Prompt Assistant browser app running at {url}")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual close path
        pass
    finally:
        server.server_close()


def _build_handler(assistant):
    class PromptAssistantHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self._send_page(_render_page(assistant=assistant))

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8")
            form = {key: values[-1] for key, values in parse_qs(raw_body).items()}

            action = form.get("action", "")
            rough_prompt = form.get("rough_prompt", "").strip()
            selected_template_id = form.get("selected_template_id", "").strip()
            extra_notes = form.get("extra_notes", "").strip()
            avoid_text = form.get("avoid_text", "").strip()
            remote_prompt = None
            library_choice = form.get("library_choice", "").strip()
            library_category = form.get("library_category", "").strip()
            remote_index = form.get("remote_index", "").strip()

            if action == "use_library":
                if library_choice.startswith("remote:"):
                    form["remote_index"] = library_choice.split(":", 1)[1]
                    action = "use_remote"
                elif library_choice.startswith("local:"):
                    selected_template_id = library_choice.split(":", 1)[1]
                    action = "use_pack"
                elif library_choice:
                    selected_template_id = library_choice
                    action = "use_pack"
            elif action == "adapt_library":
                if library_choice.startswith("remote:"):
                    form["remote_index"] = library_choice.split(":", 1)[1]
                    action = "adapt_remote"
                elif library_choice.startswith("local:"):
                    selected_template_id = library_choice.split(":", 1)[1]
                    action = "adapt_local"
                elif library_choice:
                    selected_template_id = library_choice
                    action = "adapt_local"

            if action in {"use_remote", "adapt_remote"}:
                remote_prompt = _remote_prompt_from_form(assistant, form)
                if remote_prompt:
                    if action == "use_remote":
                        rough_prompt = remote_prompt.prompt_text.strip()
                        selected_template_id = ""
                        extra_notes = ""
                        avoid_text = ""
                    else:
                        if rough_prompt:
                            extra_notes = _combine_notes(
                                extra_notes,
                                f"Reference prompt to adapt if useful:\n{remote_prompt.prompt_text}",
                            )
                        else:
                            rough_prompt = remote_prompt.prompt_text.strip()
                        selected_template_id = ""

            inspection = None
            final_prompt_result = None
            message = ""

            if action in {"use_pack", "adapt_local", "use_library_prompt"}:
                selected_template_id = form.get("template_id", "").strip() or selected_template_id

            selected_template = _find_template(selected_template_id) if selected_template_id else None

            if action == "use_library_prompt" and selected_template:
                rough_prompt = selected_template["prompt_text"].strip()
                extra_notes = ""
                avoid_text = ""
            elif action == "adapt_local" and selected_template:
                if rough_prompt:
                    extra_notes = _combine_notes(
                        extra_notes,
                        f"Reference prompt to adapt if useful:\n{selected_template['prompt_text']}",
                    )
                else:
                    rough_prompt = selected_template["prompt_text"].strip()

            if action in {"analyze", "use_pack", "build", "use_remote", "use_library", "adapt_local", "adapt_remote", "use_library_prompt"} and rough_prompt:
                inspection = assistant.inspect_prompt(prompt=rough_prompt)

            recommended_template_id = _recommended_template_id(inspection)
            if action in {"analyze", "use_remote", "use_library", "adapt_remote"} and not selected_template_id:
                selected_template_id = recommended_template_id or DEFAULT_TEMPLATE_ID

            if not selected_template and rough_prompt:
                selected_template = _find_template(recommended_template_id or DEFAULT_TEMPLATE_ID)
                selected_template_id = selected_template["id"] if selected_template else ""

            if selected_template and not rough_prompt and action in {"use_pack", "use_library", "use_library_prompt", "adapt_local"}:
                rough_prompt = selected_template["prompt_text"].strip()
                inspection = assistant.inspect_prompt(prompt=rough_prompt)
                recommended_template_id = _recommended_template_id(inspection)

            pack_values = _field_values_from_form(form, selected_template)
            if selected_template:
                pack_values = _merge_prefills(
                    current_values=pack_values,
                    template=selected_template,
                    rough_prompt=rough_prompt,
                )

            if rough_prompt and selected_template and action in {"analyze", "use_pack", "build", "use_remote", "use_library", "adapt_local", "adapt_remote", "use_library_prompt"}:
                result_lane = "refined" if action == "build" else "auto"
                if action == "use_remote":
                    result_lane = "library-remote"
                elif action in {"use_pack", "use_library", "adapt_local", "adapt_remote", "use_library_prompt"}:
                    result_lane = "library"

                final_prompt_result = _build_final_prompt_result(
                    rough_prompt=rough_prompt,
                    inspection=inspection,
                    template=selected_template,
                    field_values=pack_values,
                    extra_notes=extra_notes,
                    avoid_text=avoid_text,
                    lane=result_lane,
                )
                if action == "build":
                    message = f"Refined the final prompt with {html.escape(selected_template['title'])}."
                elif action == "use_library":
                    message = f"Loaded {html.escape(selected_template['title'])} as a ready-to-use prompt."
                elif action == "use_library_prompt":
                    message = f"Loaded {html.escape(selected_template['title'])} directly from the library."
                elif action == "adapt_local":
                    message = f"Adapted your idea using {html.escape(selected_template['title'])}."
                elif action == "adapt_remote" and remote_prompt:
                    message = f"Adapted your idea using {html.escape(remote_prompt.title)} as reference."
                elif action == "use_pack":
                    message = f"Loaded {html.escape(selected_template['title'])} into the builder."
                elif action == "use_remote" and remote_prompt:
                    message = f"Converted {html.escape(remote_prompt.title)} into a final prompt with {html.escape(selected_template['title'])}."
                else:
                    message = f"Built a final prompt from {html.escape(selected_template['title'])}."

            html_body = _render_page(
                assistant=assistant,
                rough_prompt=rough_prompt,
                inspection=inspection,
                selected_template=selected_template,
                selected_template_id=selected_template_id,
                field_values=pack_values,
                final_prompt_result=final_prompt_result,
                extra_notes=extra_notes,
                avoid_text=avoid_text,
                message=message,
                recommended_template_id=recommended_template_id,
                builder_open=action in {"use_pack", "build"} and bool(rough_prompt),
                selected_library_category=library_category,
                selected_library_choice=library_choice,
            )
            self._send_page(html_body)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def _send_page(self, page: str) -> None:
            body = page.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return PromptAssistantHandler


def _render_page(
    *,
    assistant,
    rough_prompt: str = "",
    inspection=None,
    selected_template: dict[str, Any] | None = None,
    selected_template_id: str = "",
    field_values: dict[str, str] | None = None,
    final_prompt_result: dict[str, Any] | None = None,
    extra_notes: str = "",
    avoid_text: str = "",
    message: str = "",
    recommended_template_id: str = "",
    builder_open: bool = False,
    selected_library_category: str = "",
    selected_library_choice: str = "",
) -> str:
    field_values = field_values or {}
    best_match = (inspection.recommendations[0] if inspection and inspection.recommendations else None)
    show_builder = builder_open and selected_template is not None
    library_html = _render_library_panel(
        assistant=assistant,
        rough_prompt=rough_prompt,
        best_match=best_match,
        selected_template=selected_template,
        selected_template_id=selected_template_id,
        recommended_template_id=recommended_template_id,
        selected_library_category=selected_library_category,
        selected_library_choice=selected_library_choice,
    )
    output_html = _render_output_card(final_prompt_result)
    flash = f"<div class='flash'>{message}</div>" if message else ""
    jump_script = ""
    if final_prompt_result:
        jump_script = """
        <script>
          window.addEventListener('load', function () {
            var target = document.getElementById('final-output');
            if (target) {
              target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          });
        </script>
        """

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Prompt Assistant Beta</title>
    <style>
      :root {{
        --bg: #f7f1e7;
        --panel: #fffaf4;
        --panel-strong: #fffdf9;
        --ink: #21160f;
        --muted: #6f5a49;
        --line: #e6d6c4;
        --accent: #26180f;
        --accent-soft: #efe4d4;
        --success: #365d3f;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #fcf7ef 0%, var(--bg) 100%);
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
      }}
      main {{
        max-width: 1240px;
        margin: 0 auto;
        padding: 48px 24px 80px;
      }}
      h1 {{
        margin: 0;
        font-size: clamp(2.7rem, 5vw, 4.4rem);
        line-height: 0.98;
        letter-spacing: -0.03em;
      }}
      .subcopy {{
        max-width: 820px;
        margin: 18px 0 34px;
        color: var(--muted);
        font-size: 1.15rem;
        line-height: 1.55;
      }}
      .flash {{
        margin-bottom: 18px;
        padding: 14px 18px;
        border: 1px solid #d6e4d7;
        background: #f3faf4;
        color: var(--success);
        border-radius: 18px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .panel {{
        background: rgba(255, 250, 244, 0.94);
        border: 1px solid var(--line);
        border-radius: 28px;
        box-shadow: 0 18px 50px rgba(82, 59, 32, 0.07);
      }}
      .hero,
      .card {{
        padding: 28px;
      }}
      .section-title {{
        margin: 0 0 10px;
        font-size: 2rem;
        line-height: 1.05;
      }}
      .section-copy {{
        margin: 0 0 16px;
        color: var(--muted);
        font-size: 1.04rem;
        line-height: 1.45;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      label {{
        display: block;
        margin-bottom: 10px;
        font-size: 0.95rem;
        color: var(--muted);
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      textarea,
      input[type="text"],
      select {{
        width: 100%;
        padding: 18px 20px;
        border: 1px solid #d8c4ab;
        border-radius: 20px;
        background: var(--panel-strong);
        color: var(--ink);
        font: 500 1.16rem/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        outline: none;
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
      }}
      textarea:focus,
      input[type="text"]:focus,
      select:focus {{
        border-color: #b68a51;
        box-shadow: 0 0 0 4px rgba(182, 138, 81, 0.12);
      }}
      .prompt-textarea {{
        min-height: 180px;
        resize: vertical;
      }}
      .hero-actions,
      .builder-actions {{
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        margin-top: 22px;
      }}
      button,
      .link-button {{
        appearance: none;
        border: 0;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 56px;
        padding: 0 24px;
        border-radius: 18px;
        font: 700 1.05rem/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .primary {{
        background: var(--accent);
        color: #fff7ee;
      }}
      .secondary {{
        background: var(--accent-soft);
        color: var(--accent);
      }}
      .ghost {{
        border: 1px solid var(--line);
        background: #fffdfa;
        color: var(--accent);
      }}
      .stack {{
        display: grid;
        gap: 24px;
        margin-top: 26px;
      }}
      .two-up {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 24px;
        align-items: start;
      }}
      .kicker {{
        margin: 0 0 12px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.76rem;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .metric {{
        margin: 0;
        font-size: clamp(2.4rem, 4vw, 3.2rem);
        line-height: 1;
      }}
      .progress {{
        margin: 18px 0 14px;
        height: 14px;
        border-radius: 999px;
        background: #efe4d3;
        overflow: hidden;
      }}
      .progress > span {{
        display: block;
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #d4a15b 0%, #8c5a1d 100%);
      }}
      .list {{
        margin: 14px 0 0;
        padding-left: 18px;
        color: var(--muted);
        font: 500 1rem/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .list li + li {{ margin-top: 8px; }}
      .callout {{
        margin-top: 18px;
        padding: 18px;
        border-radius: 20px;
        background: #fff4e5;
        border: 1px solid #efd7b6;
      }}
      .callout strong {{
        display: block;
        margin-bottom: 8px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .meta-row {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }}
      .tag {{
        display: inline-flex;
        align-items: center;
        padding: 8px 12px;
        border-radius: 999px;
        background: #f4eadc;
        color: var(--accent);
        font: 600 0.88rem/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .builder-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 18px;
      }}
      .field textarea {{
        min-height: 120px;
      }}
      .packs-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
      }}
      .pack-card {{
        display: grid;
        gap: 14px;
        padding: 22px;
        border-radius: 22px;
        border: 1px solid var(--line);
        background: rgba(255, 253, 249, 0.98);
      }}
      .pack-card.active {{
        border-color: #b68a51;
        box-shadow: inset 0 0 0 1px #b68a51;
      }}
      .pack-card h3 {{
        margin: 0;
        font-size: 1.35rem;
      }}
      .pack-card p {{
        margin: 0;
        color: var(--muted);
        font: 500 0.98rem/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .output-box {{
        min-height: 320px;
        white-space: pre-wrap;
        padding: 20px;
        border-radius: 22px;
        background: #fffdf9;
        border: 1px solid var(--line);
        font: 500 1rem/1.7 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .small {{
        color: var(--muted);
        font: 500 0.95rem/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .library-select {{
        min-width: 320px;
        flex: 1 1 420px;
      }}
      @media (max-width: 980px) {{
        .two-up,
        .builder-grid,
        .packs-grid {{
          grid-template-columns: 1fr;
        }}
        main {{
          padding: 28px 16px 56px;
        }}
        .hero,
        .card {{
          padding: 22px;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Prompt Assistant Beta</h1>
      <p class="subcopy">Refine prompts, find ready-made prompts, and save tokens without getting lost in a complicated workflow.</p>
      {flash}
      <section class="panel hero">
        <h2 class="section-title">Start with your rough idea</h2>
        <p class="section-copy">Use one of two actions: refine what you already wrote, or open the prompt library and grab something close to your goal.</p>
        <form method="post">
          <input type="hidden" name="action" value="analyze">
          <input type="hidden" name="selected_template_id" value="{_escape_attr(selected_template_id)}">
          <label for="rough_prompt">Rough prompt</label>
          <textarea id="rough_prompt" class="prompt-textarea" name="rough_prompt" placeholder="Example: I want to build a screenplay agent that helps writers write better screenplays using practical craft logic and trustworthy structure.">{_escape(rough_prompt)}</textarea>
          <div class="hero-actions">
            <button class="primary" type="submit">Refine Prompt</button>
            <a class="link-button secondary" href="#library">Open Prompt Library</a>
          </div>
        </form>
      </section>
      <section class="stack">
        {output_html}
        <div class="two-up">
          {_render_health_card(inspection, best_match, selected_template_id, rough_prompt, final_prompt_result)}
          {library_html}
        </div>
        {_render_pack_builder(template=selected_template, rough_prompt=rough_prompt, field_values=field_values, extra_notes=extra_notes, avoid_text=avoid_text) if show_builder else ""}
      </section>
      {jump_script}
    </main>
  </body>
</html>"""
def _render_health_card(
    inspection,
    best_match: dict[str, Any] | None,
    selected_template_id: str,
    rough_prompt: str,
    final_prompt_result: dict[str, Any] | None,
) -> str:
    if not inspection:
        return """
        <section class="panel card">
          <p class="kicker">Prompt health</p>
          <h2 class="section-title">Not checked yet</h2>
          <div class="progress"><span style="width:0%"></span></div>
          <p class="section-copy">Refine the prompt first. Then this panel will show the biggest fixes made and the most efficient version to use.</p>
        </section>
        """

    analysis = inspection.analysis
    progress_width = max(6, min(100, analysis.score))
    suggestion_list = "".join(f"<li>{_escape(item)}</li>" for item in analysis.suggestions[:3])
    token_hint = ""
    if final_prompt_result:
        most_efficient = final_prompt_result.get("most_efficient_label", "")
        savings = final_prompt_result.get("max_token_savings", 0)
        token_hint = f"""
          <div class="callout">
            <strong>Token efficiency</strong>
            <div class="small">Most compact option right now: {_escape(most_efficient)}.</div>
            <div class="small" style="margin-top:6px;">Approximate token savings versus the longest option: ~{int(savings)} input tokens.</div>
          </div>
        """

    return f"""
    <section class="panel card">
      <p class="kicker">Prompt health</p>
      <h2 class="section-title">{_escape(analysis.health_label)}</h2>
      <p class="metric">{analysis.score}/100</p>
      <div class="progress"><span style="width:{progress_width}%"></span></div>
      <p class="section-copy">A quick read on how much guesswork the original prompt still had before the app cleaned it up.</p>
      <p class="kicker">Top fixes made</p>
      <ul class="list">{suggestion_list}</ul>
      {token_hint}
    </section>
    """


def _render_builder_placeholder() -> str:
    return """
    <section class="panel card">
      <p class="kicker">Pack builder</p>
      <h2 class="section-title">Optional refinement lane</h2>
      <p class="section-copy">Analyze your idea first to get a final prompt. Then choose a pack if you want extra fields that sharpen the prompt for a specific use case.</p>
      <div class="callout">
        <strong>What happens here</strong>
        <div class="small">You will fill specific fields like audience, deliverables, or timeline. The builder then rewrites the final prompt without replacing your original idea.</div>
      </div>
    </section>
    """


def _render_library_panel(
    *,
    assistant,
    rough_prompt: str,
    best_match: dict[str, Any] | None,
    selected_template: dict[str, Any] | None,
    selected_template_id: str,
    recommended_template_id: str,
    selected_library_category: str,
    selected_library_choice: str = "",
) -> str:
    effective_category = _effective_library_category(
        selected_library_category=selected_library_category,
        rough_prompt=rough_prompt,
        best_match=best_match,
    )
    flow = _find_library_flow(effective_category)
    prompt_matches = _library_prompt_matches(
        assistant=assistant,
        rough_prompt=rough_prompt,
        flow_id=effective_category,
        best_match=best_match,
        selected_template_id=selected_template_id,
        limit=5,
    )
    total_matches = len(prompt_matches)
    category_options = _render_library_category_options(selected_flow_id=effective_category)
    prompt_cards = [
        _render_library_match_card(
            prompt_match=item,
            rough_prompt=rough_prompt,
            featured=index == 0,
            flow_id=effective_category,
        )
        for index, item in enumerate(prompt_matches)
    ]

    return f"""
    <section id="library" class="panel card">
      <p class="kicker">Library</p>
      <h2 class="section-title">Prompt library</h2>
      <p class="section-copy">Choose what you are trying to do, then pick from the 5 strongest prompt matches instead of digging through a giant list.</p>
      <form method="post">
        <input type="hidden" name="action" value="browse_library">
        <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
        <label for="library_category">What are you trying to do?</label>
        <div class="hero-actions" style="margin-top:0;">
          <select id="library_category" name="library_category" class="library-select" onchange="this.form.submit()">
            {category_options}
          </select>
        </div>
      </form>
      <div style="margin-top:24px;">
        <p class="kicker">Top prompt matches</p>
        <p class="section-copy">{_escape(flow['description'])} Showing the top {min(total_matches, 5)} of {total_matches} prompts in this category so you can choose fast.</p>
        {_render_library_card_grid(prompt_cards)}
      </div>
    </section>
    """


def _render_pack_builder(
    *,
    template: dict[str, Any] | None,
    rough_prompt: str,
    field_values: dict[str, str],
    extra_notes: str,
    avoid_text: str,
) -> str:
    if not template:
        return _render_builder_placeholder()

    fields = []
    for field_name in template["template_fields"]:
        value = field_values.get(field_name, "")
        label = FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())
        placeholder = FIELD_PLACEHOLDERS.get(field_name, "Add the detail that will make this pack more accurate.")
        if field_name in MULTILINE_FIELDS:
            input_html = f"<textarea name='pack__{_escape_attr(field_name)}' placeholder='{_escape_attr(placeholder)}'>{_escape(value)}</textarea>"
        else:
            input_html = f"<input type='text' name='pack__{_escape_attr(field_name)}' value='{_escape_attr(value)}' placeholder='{_escape_attr(placeholder)}'>"
        fields.append(
            f"""
            <div class="field">
              <label>{_escape(label)}</label>
              {input_html}
            </div>
            """
        )

    why_items = "".join(f"<li>{_escape(item)}</li>" for item in template["why_it_works"][:3])
    hint_items = "".join(f"<li>{_escape(item)}</li>" for item in template["repair_hints"][:3])

    return f"""
    <section class="panel card">
      <p class="kicker">Pack builder</p>
      <h2 class="section-title">{_escape(template['title'])}</h2>
      <p class="section-copy">{_escape(template['summary'])}</p>
      <div class="meta-row">
        <span class="tag">{_escape(template['category'])}</span>
        <span class="tag">{_escape(template['pack'])}</span>
        <span class="tag">{_escape(template['subcategory'])}</span>
      </div>
      <div class="two-up" style="grid-template-columns:1fr 1fr; gap:18px; margin-top:18px;">
        <div>
          <p class="kicker">Why this pack works</p>
          <ul class="list">{why_items}</ul>
        </div>
        <div>
          <p class="kicker">What to strengthen</p>
          <ul class="list">{hint_items}</ul>
        </div>
      </div>
      <form method="post">
        <input type="hidden" name="action" value="build">
        <input type="hidden" name="selected_template_id" value="{_escape_attr(template['id'])}">
        <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
        <div class="builder-grid">
          {''.join(fields)}
        </div>
        <div class="builder-grid" style="margin-top:16px;">
          <div class="field">
            <label>Extra notes (optional)</label>
            <textarea name="extra_notes" placeholder="Add anything the final prompt should remember.">{_escape(extra_notes)}</textarea>
          </div>
          <div class="field">
            <label>Avoid (optional)</label>
            <textarea name="avoid_text" placeholder="Example: avoid generic tone, avoid hype, avoid too much jargon.">{_escape(avoid_text)}</textarea>
          </div>
        </div>
        <div class="builder-actions">
          <button class="primary" type="submit">Refine Final Prompt</button>
          <a class="link-button ghost" href="#starter-packs">Try a different pack</a>
        </div>
      </form>
    </section>
    """


def _render_recommendation_banner(*, rough_prompt: str, best_match: dict[str, Any] | None, selected_template_id: str) -> str:
    if not best_match:
        return ""
    template_id = best_match.get("template_id", "")
    if not template_id or template_id == selected_template_id:
        return ""
    return f"""
    <section class="panel card">
      <p class="kicker">Suggested switch</p>
      <h2 class="section-title">This idea may fit a better pack</h2>
      <p class="section-copy">{_escape(best_match.get('title', ''))} looks closer to what you are trying to do. Use it if you want a smarter set of refinement fields.</p>
      <form method="post" class="hero-actions" style="margin-top:0;">
        <input type="hidden" name="action" value="use_pack">
        <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
        <input type="hidden" name="template_id" value="{_escape_attr(template_id)}">
        <button class="secondary" type="submit">Use Suggested Pack</button>
      </form>
    </section>
    """


def _render_library_category_options(*, selected_flow_id: str) -> str:
    options = []
    for flow in LIBRARY_FLOWS:
        selected = " selected" if flow["id"] == selected_flow_id else ""
        options.append(f"<option value='{_escape_attr(flow['id'])}'{selected}>{_escape(flow['label'])}</option>")
    return "".join(options)


def _find_library_flow(flow_id: str) -> dict[str, Any]:
    for flow in LIBRARY_FLOWS:
        if flow["id"] == flow_id:
            return flow
    return LIBRARY_FLOWS[0]


def _effective_library_category(*, selected_library_category: str, rough_prompt: str, best_match: dict[str, Any] | None) -> str:
    if selected_library_category:
        return selected_library_category
    if best_match:
        return _flow_id_for_pack(best_match.get("pack", ""))
    lowered = rough_prompt.lower()
    for flow in LIBRARY_FLOWS:
        if any(keyword in lowered for keyword in flow["keywords"]):
            return flow["id"]
    return "general_use"


def _flow_id_for_pack(pack_name: str) -> str:
    mapping = {
        "Product Strategy Pack": "mvp_building",
        "Business Idea Validation Pack": "validation_research",
        "Proposal Pack": "proposals_client_work",
        "Meeting Summary Pack": "productivity_planning",
        "Blog Outline Pack": "content_seo",
        "Email Writing Pack": "sales_outreach",
        "Code Explainer Pack": "coding_help",
        "Bug Fix Pack": "debugging_fixes",
        "Study Guide Pack": "study_learning",
        "Paper Summary Pack": "research_summaries",
        "Story Idea Pack": "story_screenplay",
        "General Prompt Repair Pack": "prompt_repair",
    }
    return mapping.get(pack_name, "general_use")


def _library_prompt_candidates(
    *,
    assistant,
    rough_prompt: str,
    flow_id: str,
    best_match: dict[str, Any] | None,
    selected_template_id: str,
    limit: int,
) -> tuple[list[str], int]:
    prompt_matches = _library_prompt_matches(
        assistant=assistant,
        rough_prompt=rough_prompt,
        flow_id=flow_id,
        best_match=best_match,
        selected_template_id=selected_template_id,
        limit=limit,
    )
    total_matches = len(prompt_matches)
    top_cards = [_render_library_match_card(prompt_match=item, rough_prompt=rough_prompt, featured=False, flow_id=flow_id) for item in prompt_matches]
    if top_cards and best_match:
        for idx, card in enumerate(top_cards):
            if "Best fit right now" in card:
                top_cards.insert(0, top_cards.pop(idx))
                break
    elif top_cards:
        top_cards[0] = top_cards[0].replace("<article class=\"pack-card", "<article class=\"pack-card active", 1).replace(
            "<span class=\"tag\">Library</span>",
            "<span class=\"tag\">Best fit right now</span><span class=\"tag\">Library</span>",
            1,
        ) if "Open Source" not in top_cards[0] else top_cards[0].replace(
            "<article class=\"pack-card",
            "<article class=\"pack-card active",
            1,
        ).replace(
            "<span class=\"tag\">Open Source</span>",
            "<span class=\"tag\">Best fit right now</span><span class=\"tag\">Open Source</span>",
            1,
        )
    return top_cards, total_matches


def _library_prompt_matches(
    *,
    assistant,
    rough_prompt: str,
    flow_id: str,
    best_match: dict[str, Any] | None,
    selected_template_id: str,
    limit: int,
) -> list[dict[str, Any]]:
    flow = _find_library_flow(flow_id)
    query_terms = _library_query_terms(rough_prompt, flow["keywords"])
    prompts: list[dict[str, Any]] = []

    for prompt in assistant.library.local_prompts():
        if not _prompt_matches_flow(prompt=prompt, flow=flow):
            continue
        template_id = _template_id_from_prompt(prompt)
        if template_id == selected_template_id:
            continue
        score = _score_library_prompt(prompt=prompt, query_terms=query_terms, flow=flow, best_match=best_match)
        prompts.append(
            {
                "score": score,
                "origin": prompt.origin,
                "choice": f"local:{template_id}",
                "title": prompt.title,
                "summary": prompt.summary,
                "preview": _compact_preview(prompt.prompt_text),
                "subcategory": prompt.subcategory,
                "source_label": "Library",
                "prompt": prompt,
            }
        )

    for index, prompt in enumerate(assistant.library.cached_remote_prompts()):
        if not _prompt_matches_flow(prompt=prompt, flow=flow):
            continue
        score = _score_library_prompt(prompt=prompt, query_terms=query_terms, flow=flow, best_match=best_match)
        prompts.append(
            {
                "score": score,
                "origin": prompt.origin,
                "choice": f"remote:{index}",
                "title": prompt.title,
                "summary": prompt.summary or _compact_preview(prompt.prompt_text),
                "preview": _compact_preview(prompt.prompt_text),
                "subcategory": prompt.subcategory,
                "source_label": "Open Source",
                "prompt": prompt,
            }
        )

    prompts.sort(key=lambda item: (-item["score"], 0 if item["origin"] == "local" else 1, item["title"]))
    return prompts[:limit]


def _render_library_card_grid(cards: list[str]) -> str:
    if not cards:
        return "<div class='callout'><strong>No prompt matches yet</strong><div class='small'>Try another category or refine your rough prompt first so the app can rank better matches.</div></div>"
    return f"<div class='packs-grid'>{''.join(cards)}</div>"


def _render_library_choice_options(*, prompt_matches: list[dict[str, Any]], selected_choice: str) -> str:
    options = []
    for item in prompt_matches:
        selected = " selected" if item["choice"] == selected_choice else ""
        label = f"{item['title']} — {item['subcategory']}"
        options.append(f"<option value='{_escape_attr(item['choice'])}'{selected}>{_escape(label)}</option>")
    return "".join(options)


def _render_library_preview_card(prompt_match: dict[str, Any]) -> str:
    return f"""
    <article class="pack-card active">
      <div class="meta-row">
        <span class="tag">Best fit right now</span>
        <span class="tag">{_escape(prompt_match['source_label'])}</span>
        <span class="tag">{_escape(prompt_match['subcategory'])}</span>
      </div>
      <h3>{_escape(prompt_match['title'])}</h3>
      <p>{_escape(prompt_match['summary'])}</p>
      <p class="small">{_escape(prompt_match['preview'])}</p>
    </article>
    """


def _render_library_match_card(*, prompt_match: dict[str, Any], rough_prompt: str, featured: bool, flow_id: str) -> str:
    active = " active" if featured else ""
    best_tag = "<span class=\"tag\">Best fit right now</span>" if featured else ""
    choice = prompt_match["choice"]
    use_action = "use_library"
    adapt_action = "adapt_library"
    return f"""
    <article class="pack-card{active}">
      <div class="meta-row">
        {best_tag}
        <span class="tag">{_escape(prompt_match['source_label'])}</span>
        <span class="tag">{_escape(prompt_match['subcategory'])}</span>
      </div>
      <h3>{_escape(prompt_match['title'])}</h3>
      <p>{_escape(prompt_match['summary'])}</p>
      <p class="small">{_escape(prompt_match['preview'])}</p>
      <div class="hero-actions" style="margin-top:0;">
        <form method="post">
          <input type="hidden" name="action" value="{use_action}">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="library_choice" value="{_escape_attr(choice)}">
          <button class="ghost" type="submit">Use Prompt</button>
        </form>
        <form method="post">
          <input type="hidden" name="action" value="{adapt_action}">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="library_choice" value="{_escape_attr(choice)}">
          <button class="secondary" type="submit">Adapt to My Need</button>
        </form>
      </div>
    </article>
    """


def _library_query_terms(rough_prompt: str, flow_keywords: set[str]) -> set[str]:
    terms = {term.lower() for term in re.findall(r"[a-zA-Z0-9']+", rough_prompt) if len(term) >= 4}
    terms.update(keyword.lower() for keyword in flow_keywords if " " not in keyword)
    return terms


def _prompt_matches_flow(*, prompt: LibraryPrompt, flow: dict[str, Any]) -> bool:
    matched_flow_ids = classify_library_flow_ids(
        title=prompt.title,
        prompt_text=prompt.prompt_text,
        pack=prompt.pack,
        subcategory=prompt.subcategory,
        domain=prompt.domain,
        interest=prompt.interest,
    )
    return flow["id"] in matched_flow_ids


def _score_library_prompt(*, prompt: LibraryPrompt, query_terms: set[str], flow: dict[str, Any], best_match: dict[str, Any] | None) -> int:
    blob = " ".join(
        [
            prompt.title,
            prompt.summary,
            prompt.prompt_text,
            prompt.pack,
            prompt.subcategory,
            prompt.domain,
            prompt.interest,
            " ".join(prompt.keywords),
        ]
    ).lower()
    score = 10 if prompt.origin == "local" else 6
    if prompt.pack in flow["packs"]:
        score += 14
    if best_match:
        if prompt.pack == best_match.get("pack"):
            score += 10
        if prompt.subcategory == best_match.get("subcategory"):
            score += 4
        if prompt.title == best_match.get("title"):
            score += 8
    score += sum(3 for term in query_terms if term in prompt.title.lower())
    score += sum(2 for term in query_terms if term in blob)
    return score


def _template_id_from_prompt(prompt: LibraryPrompt) -> str:
    for pack in PACK_CATALOG:
        if pack["pack"] != prompt.pack:
            continue
        for template in pack["templates"]:
            if template["title"] == prompt.title and template["subcategory"] == prompt.subcategory:
                return template["id"]
    return ""


def _render_local_library_card(*, prompt: LibraryPrompt, rough_prompt: str, featured: bool, flow_id: str) -> str:
    template_id = _template_id_from_prompt(prompt)
    active = " active" if featured else ""
    best_tag = "<span class=\"tag\">Best fit right now</span>" if featured else ""
    return f"""
    <article class="pack-card{active}">
      <div class="meta-row">
        {best_tag}
        <span class="tag">Library</span>
        <span class="tag">{_escape(prompt.subcategory)}</span>
      </div>
      <h3>{_escape(prompt.title)}</h3>
      <p>{_escape(prompt.summary)}</p>
      <div class="hero-actions" style="margin-top:0;">
        <form method="post">
          <input type="hidden" name="action" value="use_library_prompt">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="template_id" value="{_escape_attr(template_id)}">
          <button class="ghost" type="submit">Use Prompt</button>
        </form>
        <form method="post">
          <input type="hidden" name="action" value="adapt_local">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="template_id" value="{_escape_attr(template_id)}">
          <button class="secondary" type="submit">Adapt to My Need</button>
        </form>
      </div>
    </article>
    """


def _render_remote_library_card(*, prompt: LibraryPrompt, rough_prompt: str, index: int, featured: bool, flow_id: str) -> str:
    preview = _compact_preview(prompt.prompt_text)
    active = " active" if featured else ""
    best_tag = "<span class=\"tag\">Best fit right now</span>" if featured else ""
    return f"""
    <article class="pack-card{active}">
      <div class="meta-row">
        {best_tag}
        <span class="tag">Open Source</span>
        <span class="tag">{_escape(prompt.subcategory)}</span>
      </div>
      <h3>{_escape(prompt.title)}</h3>
      <p>{_escape(prompt.summary or preview)}</p>
      <p class="small">{_escape(preview)}</p>
      <div class="hero-actions" style="margin-top:0;">
        <form method="post">
          <input type="hidden" name="action" value="use_remote">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="remote_index" value="{index}">
          <button class="ghost" type="submit">Use Prompt</button>
        </form>
        <form method="post">
          <input type="hidden" name="action" value="adapt_remote">
          <input type="hidden" name="rough_prompt" value="{_escape_attr(rough_prompt)}">
          <input type="hidden" name="library_category" value="{_escape_attr(flow_id)}">
          <input type="hidden" name="remote_index" value="{index}">
          <button class="secondary" type="submit">Adapt to My Need</button>
        </form>
      </div>
    </article>
    """


def _render_output_card(final_prompt_result: dict[str, Any] | None) -> str:
    if not final_prompt_result:
        return """
        <section class="panel card">
          <p class="kicker">Final output</p>
          <h2 class="section-title">Your final prompt will appear here</h2>
          <p class="section-copy">Refine your rough prompt first. Then choose the most efficient version or open the library if you want to adapt an existing prompt.</p>
          <div class="output-box">This area will show the final working prompt the app builds for you, plus lower-cost and deeper alternatives.</div>
        </section>
        """

    if final_prompt_result["lane"] == "auto":
        lane_copy = "This is the first ready-to-use final prompt built from your rough idea."
    elif final_prompt_result["lane"] == "library-remote":
        lane_copy = "This final prompt was built from an open-source reference and adapted into the app's structure."
    else:
        lane_copy = "This is the refined final prompt rebuilt after you selected or adapted a library item."
    why_items = "".join(f"<li>{_escape(item)}</li>" for item in final_prompt_result["why"][:5])
    alternate_cards = "".join(
        f"""
        <article class="pack-card" style="gap:10px;">
          <div class="meta-row">
            <span class="tag">{_escape(option['label'])}</span>
            <span class="tag">~{int(option['approx_tokens'])} input tokens</span>
            {"<span class='tag'>Most token-efficient</span>" if option.get("most_efficient") else ""}
          </div>
          <p class="small">{_escape(option['best_for'])}</p>
          <div class="output-box" style="min-height:180px; font-size:0.95rem;">{_escape(option['content'])}</div>
        </article>
        """
        for option in final_prompt_result["alternate_options"]
    )
    source_label = "Open Source" if final_prompt_result["lane"] == "library-remote" else "Library"
    return f"""
    <section id="final-output" class="panel card">
      <p class="kicker">Final output</p>
      <h2 class="section-title">Final prompt ready</h2>
      <p class="section-copy">{_escape(lane_copy)}</p>
      <div class="meta-row" style="margin-bottom:14px;">
        <span class="tag">Primary structure: {_escape(final_prompt_result['primary_archetype_label'])}</span>
        <span class="tag">{_escape(source_label)}</span>
        <span class="tag">~{int(final_prompt_result['final_prompt_tokens'])} input tokens</span>
        {"<span class='tag'>Most token-efficient</span>" if final_prompt_result.get("primary_most_efficient") else ""}
      </div>
      <div class="output-box">{_escape(final_prompt_result['final_prompt'])}</div>
      <div style="margin-top:18px;">
        <p class="kicker">Why this version works better</p>
        <ul class="list">{why_items}</ul>
      </div>
      <div class="callout" style="margin-top:18px;">
        <strong>Approximate token savings</strong>
        <div class="small">The most compact prompt option on this screen is {_escape(final_prompt_result['most_efficient_label'])}.</div>
        <div class="small" style="margin-top:6px;">Choosing that option instead of the longest one may save about ~{int(final_prompt_result['max_token_savings'])} input tokens.</div>
      </div>
      <div style="margin-top:24px;">
        <p class="kicker">Other useful prompt options</p>
        <p class="section-copy">Use the main final prompt first. These alternates show the cost and trade-off of going shorter or deeper.</p>
        <div class="packs-grid">{alternate_cards}</div>
      </div>
    </section>
    """


def _field_values_from_form(form: dict[str, str], template: dict[str, Any] | None) -> dict[str, str]:
    if not template:
        return {}
    values: dict[str, str] = {}
    for field in template["template_fields"]:
        values[field] = form.get(f"pack__{field}", "").strip()
    return values


def _merge_prefills(*, current_values: dict[str, str], template: dict[str, Any], rough_prompt: str) -> dict[str, str]:
    values = dict(current_values)
    for field in template["template_fields"]:
        if values.get(field):
            continue
        inferred = _prefill_field(field, rough_prompt, template)
        if inferred:
            values[field] = inferred
    return values


def _prefill_field(field_name: str, rough_prompt: str, template: dict[str, Any]) -> str:
    text = " ".join(rough_prompt.split())
    if not text:
        return ""
    lowered = text.lower()
    if field_name in {"topic", "paper_topic", "initiative", "concept", "task", "service", "product", "offer", "premise"}:
        return _extract_subject_phrase(text, field_name, template["pack"])
    if field_name in {"audience", "recipient_role", "client_type", "stakeholders"}:
        return _extract_audience_phrase(lowered, text)
    if field_name in {"deliverables", "components", "key_topics", "topics"}:
        return _extract_phrase(lowered, text, [" with ", " including ", " that includes "])
    if field_name in {"timeline", "timeframe", "time_available", "exam_date"}:
        return _extract_phrase(lowered, text, [" by ", " within ", " in "])
    if field_name in {"goal", "desired_action", "cta", "expected_outcome"}:
        return _goal_hint(text, template["pack"])
    if field_name == "tone":
        return "clear and practical"
    if field_name == "search_intent":
        return "inform and persuade"
    if field_name == "format":
        return _default_format_for_pack(template["pack"])
    return ""


def _extract_phrase(lowered: str, original: str, markers: list[str]) -> str:
    for marker in markers:
        idx = lowered.find(marker)
        if idx == -1:
            continue
        start = idx + len(marker)
        tail = _trim_clause(original[start:])
        if tail:
            return tail
    return ""


def _extract_audience_phrase(lowered: str, original: str) -> str:
    if "writer" in lowered and "director" in lowered:
        return "writers and directors"
    value = _extract_phrase(lowered, original, [" for ", " to "])
    if value and not _looks_like_product_phrase(value):
        return value
    return ""


def _extract_subject_phrase(original: str, field_name: str, pack_name: str) -> str:
    text = _strip_preface(original)
    lowered = text.lower()

    if pack_name in {"Product Strategy Pack", "Business Idea Validation Pack"}:
        if "platform" in lowered:
            return _trim_clause(_capture_tail(text, ["build ", "create ", "make ", "develop "]) or text)
        if "website" in lowered or "app" in lowered:
            return _trim_clause(_capture_tail(text, ["build ", "create ", "make ", "develop "]) or text)
        if field_name in {"topic", "initiative", "concept"}:
            return _trim_clause(text)

    if field_name in {"service", "product", "offer"}:
        captured = _capture_tail(text, ["build ", "create ", "make ", "develop ", "launch ", "design "])
        if captured:
            return _trim_clause(captured)

    return _trim_clause(text)


def _capture_tail(original: str, verbs: list[str]) -> str:
    lowered = original.lower()
    for verb in verbs:
        idx = lowered.find(verb)
        if idx != -1:
            return original[idx + len(verb) :]
    return ""


def _looks_like_product_phrase(value: str) -> bool:
    lowered = value.lower()
    return any(
        word in lowered
        for word in ["website", "platform", "app", "product", "service", "tool", "software", "agent"]
    )


def _trim_clause(text: str) -> str:
    chunk = text.strip(" .,:;-")
    for separator in [" and ", ". ", ", ", " with ", " while ", " but "]:
        idx = chunk.lower().find(separator)
        if idx > 0:
            chunk = chunk[:idx]
            break
    return chunk.strip(" .,:;-")


def _strip_preface(text: str) -> str:
    cleaned = re.sub(r"^(i want to|i need to|help me|please)\s+", "", text.strip(), flags=re.IGNORECASE)
    return cleaned[:180].strip()


def _goal_hint(text: str, pack_name: str) -> str:
    lowered = text.lower()
    if pack_name == "Product Strategy Pack":
        return "clarify the product direction, audience, and strongest differentiators"
    if pack_name == "Business Idea Validation Pack":
        return "evaluate the opportunity, risks, and whether the idea is worth pursuing"
    if "website" in lowered or "landing page" in lowered:
        return "help the reader understand the offer and take the next step"
    if "proposal" in lowered:
        return "make the proposal decision-ready"
    if "email" in lowered:
        return "get a clear reply"
    if "bug" in lowered or "fix" in lowered:
        return "find the likely cause and a safe fix"
    if "study" in lowered or "exam" in lowered:
        return "make the topic easier to remember"
    if "story" in lowered or "screenplay" in lowered or "script" in lowered:
        return "create a stronger narrative direction"
    if pack_name == "General Prompt Repair Pack":
        return "produce a clear, usable answer"
    return "produce a clear, usable answer"


def _default_format_for_pack(pack_name: str) -> str:
    formats = {
        "Blog Outline Pack": "headline plus structured sections",
        "Email Writing Pack": "short email draft",
        "Product Strategy Pack": "strategy brief with priorities",
        "Business Idea Validation Pack": "validation brief with risks and recommendation",
        "Proposal Pack": "proposal sections",
        "Meeting Summary Pack": "summary plus action items",
        "Code Explainer Pack": "step-by-step explanation",
        "Bug Fix Pack": "debug plan",
        "Study Guide Pack": "study guide with bullets",
        "Paper Summary Pack": "plain-language summary",
        "Story Idea Pack": "outline",
        "General Prompt Repair Pack": "structured prompt",
    }
    return formats.get(pack_name, "structured output")


def _build_final_prompt_result(
    *,
    rough_prompt: str,
    inspection,
    template: dict[str, Any],
    field_values: dict[str, str],
    extra_notes: str,
    avoid_text: str,
    lane: str,
) -> dict[str, Any]:
    filled_template = _fill_template_with_fallbacks(
        template_text=template["prompt_text"],
        field_values=field_values,
        template=template,
        rough_prompt=rough_prompt,
    )
    output_type = _first_non_empty(field_values.get("format"), _default_format_for_pack(template["pack"]))
    tone = _first_non_empty(field_values.get("tone"), "clear and practical")
    audience = _first_non_empty(
        field_values.get("audience"),
        field_values.get("client_type"),
        field_values.get("recipient_role"),
        field_values.get("stakeholders"),
    )

    primary_instruction = _primary_instruction(
        template=template,
        rough_prompt=rough_prompt,
        filled_template=filled_template,
        field_values=field_values,
    )
    shared = _shared_prompt_context(
        rough_prompt=rough_prompt,
        template=template,
        primary_instruction=primary_instruction,
        audience=audience,
        tone=tone,
        output_type=output_type,
        extra_notes=extra_notes,
        avoid_text=avoid_text,
        field_values=field_values,
    )
    primary_archetype_id, alternate_ids = _select_archetypes(
        rough_prompt=rough_prompt,
        template=template,
        output_type=output_type,
        inspection=inspection,
    )
    final_prompt = _build_archetype_prompt(primary_archetype_id, shared)
    why = list(template.get("why_it_works", []))[:3]
    if inspection and inspection.analysis.gaps:
        why.append(f"Fixed missing pieces such as: {', '.join(inspection.analysis.gaps[:2]).lower()}.")
    why.append(f"Uses the {template['title']} starter pack as the base.")
    why.append(f"Locks in a clearer output format: {output_type}.")
    final_prompt_tokens = _estimate_prompt_tokens(final_prompt)
    alternate_options = [
        {
            "id": archetype_id,
            "label": PROMPT_ARCHETYPES[archetype_id]["label"],
            "best_for": PROMPT_ARCHETYPES[archetype_id]["best_for"],
            "content": _build_archetype_prompt(archetype_id, shared),
            "approx_tokens": _estimate_prompt_tokens(_build_archetype_prompt(archetype_id, shared)),
        }
        for archetype_id in alternate_ids
    ]
    token_options = [{"label": "Primary Final Prompt", "tokens": final_prompt_tokens, "is_primary": True}] + [
        {"label": option["label"], "tokens": option["approx_tokens"], "is_primary": False}
        for option in alternate_options
    ]
    most_efficient = min(token_options, key=lambda item: item["tokens"])
    longest = max(token_options, key=lambda item: item["tokens"])
    for option in alternate_options:
        option["most_efficient"] = option["label"] == most_efficient["label"] and not most_efficient["is_primary"]
    return {
        "final_prompt": final_prompt,
        "lane": lane,
        "template_title": template["title"],
        "pack": template["pack"],
        "why": why,
        "primary_archetype": primary_archetype_id,
        "primary_archetype_label": PROMPT_ARCHETYPES[primary_archetype_id]["label"],
        "final_prompt_tokens": final_prompt_tokens,
        "primary_most_efficient": bool(most_efficient["is_primary"]),
        "most_efficient_label": most_efficient["label"],
        "max_token_savings": max(0, longest["tokens"] - most_efficient["tokens"]),
        "alternate_options": alternate_options,
    }


def _primary_instruction(
    *,
    template: dict[str, Any],
    rough_prompt: str,
    filled_template: str,
    field_values: dict[str, str],
) -> str:
    if template["pack"] == "General Prompt Repair Pack":
        base = _sentence_case(_strip_preface(rough_prompt) or filled_template)
        goal = _first_non_empty(
            field_values.get("goal"),
            field_values.get("decision_goal"),
            field_values.get("expected_outcome"),
            field_values.get("cta"),
            field_values.get("desired_action"),
        )
        if goal and goal.lower() not in base.lower():
            base = f"{base} The goal is to {goal}."
        return base
    return _sentence_case(filled_template)


def _sentence_case(text: str) -> str:
    cleaned = " ".join(text.split()).strip()
    if not cleaned:
        return cleaned
    cleaned = cleaned[0].upper() + cleaned[1:]
    if cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _shared_prompt_context(
    *,
    rough_prompt: str,
    template: dict[str, Any],
    primary_instruction: str,
    audience: str,
    tone: str,
    output_type: str,
    extra_notes: str,
    avoid_text: str,
    field_values: dict[str, str],
) -> dict[str, Any]:
    role = _role_for_pack(template["pack"])
    goal = _first_non_empty(
        field_values.get("goal"),
        field_values.get("decision_goal"),
        field_values.get("expected_outcome"),
        field_values.get("desired_action"),
        field_values.get("cta"),
        _goal_hint(rough_prompt, template["pack"]),
    )
    context_lines = [
        f"Original user request: {rough_prompt}",
        f"Matched starter pack: {template['title']} from {template['pack']}",
    ]
    if audience:
        context_lines.append(f"Audience: {audience}")
    if extra_notes:
        context_lines.append(f"Extra notes: {extra_notes}")
    instruction_lines = [
        f"Keep the answer {tone}.",
        f"Return the result as {output_type}.",
        *template.get("repair_hints", [])[:2],
    ]
    if avoid_text:
        instruction_lines.append(f"Avoid: {avoid_text}.")
    data_lines = []
    for key, value in field_values.items():
        if value:
            label = FIELD_LABELS.get(key, key.replace('_', ' ').title())
            data_lines.append(f"{label}: {value}")
    if not data_lines:
        data_lines.append(f"Working base: {primary_instruction}")
    return {
        "role": role,
        "task": primary_instruction,
        "goal": goal,
        "context_lines": context_lines,
        "instruction_lines": instruction_lines,
        "data_lines": data_lines,
        "output_type": output_type,
        "audience": audience,
    }


def _role_for_pack(pack_name: str) -> str:
    roles = {
        "Blog Outline Pack": "You are a senior content strategist and editor.",
        "Email Writing Pack": "You are an expert email copywriter focused on clear conversion-driven writing.",
        "Product Strategy Pack": "You are a senior product strategist who turns early ideas into sharper product decisions.",
        "Business Idea Validation Pack": "You are a pragmatic startup analyst who tests business ideas against real market logic.",
        "Proposal Pack": "You are a strategic proposal writer who makes ideas decision-ready.",
        "Meeting Summary Pack": "You are a sharp chief of staff who turns messy notes into useful decisions and actions.",
        "Code Explainer Pack": "You are a senior software engineer and technical explainer.",
        "Bug Fix Pack": "You are a senior debugging engineer focused on safe fixes and clear reasoning.",
        "Study Guide Pack": "You are a patient expert tutor who explains things clearly and practically.",
        "Paper Summary Pack": "You are a research analyst who turns dense material into grounded summaries.",
        "Story Idea Pack": "You are a story development partner with strong craft instincts.",
        "General Prompt Repair Pack": "You are an expert prompt architect who turns rough ideas into strong prompts.",
    }
    return roles.get(pack_name, "You are an expert prompt architect.")


def _select_archetypes(*, rough_prompt: str, template: dict[str, Any], output_type: str, inspection) -> tuple[str, list[str]]:
    text = f"{rough_prompt} {template['pack']} {template['title']} {output_type}".lower()
    if any(word in text for word in ["image", "visual", "video", "shot", "cinematic", "thumbnail", "storyboard"]):
        return "visual_director", ["logical_text", "deep_reasoning", "operator_brief"]
    if any(word in text for word in ["research", "industry", "market", "analysis", "investor", "paper", "study", "validation"]):
        return "analyst_brief", ["logical_text", "deep_reasoning", "operator_brief"]
    if template["pack"] in {"Product Strategy Pack", "Business Idea Validation Pack"}:
        return "analyst_brief", ["logical_text", "deep_reasoning", "operator_brief"]
    if template["pack"] in {"Paper Summary Pack", "Meeting Summary Pack"}:
        return "analyst_brief", ["logical_text", "deep_reasoning", "operator_brief"]
    if template["pack"] == "General Prompt Repair Pack" and inspection and inspection.analysis.score < 70:
        return "operator_brief", ["logical_text", "deep_reasoning", "analyst_brief"]
    if template["pack"] == "Story Idea Pack":
        return "deep_reasoning", ["logical_text", "operator_brief", "visual_director"]
    return "logical_text", ["operator_brief", "deep_reasoning", "analyst_brief"]


def _build_archetype_prompt(archetype_id: str, shared: dict[str, Any]) -> str:
    role = shared["role"]
    task = shared["task"]
    goal = shared["goal"] or "produce a clear, usable answer"
    context_block = "\n".join(f"- {item}" for item in shared["context_lines"])
    instruction_block = "\n".join(f"- {item}" for item in shared["instruction_lines"])
    data_block = "\n".join(f"- {item}" for item in shared["data_lines"])
    output_type = shared["output_type"]

    if archetype_id == "operator_brief":
        return "\n".join(
            [
                f"Role:\n{role}",
                f"\nTask:\n{task}",
                f"\nInstruction:\n{instruction_block}",
                f"\nData:\n{data_block}",
                f"\nOutput Format:\n- Return the result as {output_type}.",
            ]
        ).strip()

    if archetype_id == "deep_reasoning":
        return "\n".join(
            [
                f"Task:\n{task}",
                f"\nContext:\n{context_block}",
                f"\nSuccess Brief:\n- Goal: {goal}\n- Audience: {shared['audience'] or 'the intended audience'}\n- Output type: {output_type}",
                f"\nRules:\n{instruction_block}",
                "\nOutput:\n- Give the answer in a way that is directly usable without extra explanation.",
            ]
        ).strip()

    if archetype_id == "analyst_brief":
        return "\n".join(
            [
                f"Role:\n{role}",
                f"\nPurpose:\n{task}",
                f"\nEvidence & Discipline:\n{context_block}\n{data_block}",
                f"\nRules:\n{instruction_block}",
                f"\nOutput Structure:\n- Return the answer as {output_type}.\n- Make trade-offs, assumptions, and limits explicit.",
            ]
        ).strip()

    if archetype_id == "visual_director":
        return "\n".join(
            [
                f"Subject:\n{task}",
                f"\nContext:\n{context_block}",
                "\nDirection:\n- Describe composition, motion, atmosphere, and visual clarity.\n- Keep the output cinematic, specific, and coherent.",
                f"\nConstraints:\n{instruction_block}",
                f"\nOutput Format:\n- Return the result as {output_type}.",
            ]
        ).strip()

    return "\n".join(
        [
            f"Role:\n{role}",
            f"\nContext:\n{context_block}",
            f"\nTask:\n{task}",
            f"\nRules:\n{instruction_block}",
            f"\nFormat:\n- Return the result as {output_type}.",
        ]
    ).strip()


def _fill_template_with_fallbacks(
    *,
    template_text: str,
    field_values: dict[str, str],
    template: dict[str, Any],
    rough_prompt: str,
) -> str:
    result = template_text
    placeholders = re.findall(r"\[([a-zA-Z0-9_]+)\]", template_text)
    for key in placeholders:
        replacement = (
            field_values.get(key, "").strip()
            or _prefill_field(key, rough_prompt, template)
            or _fallback_for_field(key, template["pack"])
        )
        result = result.replace(f"[{key}]", replacement)
    return " ".join(result.split())


def _fallback_for_field(field_name: str, pack_name: str) -> str:
    fallback_map = {
        "audience": "the intended audience",
        "call_goal": "move the conversation forward clearly",
        "character_type": "main character",
        "client_name": "the client",
        "client_type": "the client",
        "code_goal": "solve the main technical problem",
        "comparison_goal": "show the most useful differences",
        "components": "the important components",
        "concept": "the core concept",
        "conflict": "the central tension",
        "constraints": "keep it clear, specific, and practical",
        "core_opinion": "a clear point of view",
        "cta": "take the next logical step",
        "deliverables": "the key deliverables",
        "desired_action": "take the next logical step",
        "done_definition": "a clear, complete result",
        "ending_type": "a satisfying ending",
        "environment": "the current environment",
        "exam_date": "the upcoming exam",
        "example_type": "simple real-world",
        "expected_behavior": "the correct expected behavior",
        "expected_outcome": "a useful, decision-ready result",
        "flaw": "a believable flaw",
        "focus_area": "the most important area",
        "follow_up": "the right next step",
        "format": _default_format_for_pack(pack_name),
        "goal": "produce a clear, usable answer",
        "initiative": "the proposed initiative",
        "key_topics": "the most important topics",
        "language": "the relevant language",
        "level": "beginner",
        "main_benefit": "the clearest benefit",
        "main_risk": "the biggest risk",
        "main_takeaway": "the main takeaway",
        "meeting_goal": "the meeting objective",
        "offer": "the offer",
        "pain_point": "the main pain point",
        "paper_set": "the selected papers",
        "paper_topic": "the paper topic",
        "premise": "the core premise",
        "pricing_model": "a practical pricing model",
        "product": "the product or service",
        "proof": "a credible proof point",
        "proof_points": "the strongest proof points",
        "protagonist": "the main character",
        "recipient_role": "the intended reader",
        "repro_steps": "the clearest reproduction steps",
        "research_gap": "the likely research gap",
        "risky_area": "the riskiest area",
        "scene_goal": "the scene objective",
        "search_intent": "inform and persuade",
        "service": "the service",
        "setting": "the setting",
        "sources": "the available sources",
        "stakeholders": "the stakeholders",
        "stakes": "the main stakes",
        "stack": "the current stack",
        "symptom": "the main symptom",
        "system_area": "the affected system area",
        "system_goal": "the system goal",
        "task": "the core task",
        "team_name": "the team",
        "test_focus": "the most important tests",
        "themes": "the main themes",
        "time_available": "the available time",
        "timeframe": "a realistic timeframe",
        "timeline": "a realistic timeline",
        "tone": "clear and practical",
        "topic": "the core topic",
        "topics": "the main topics",
        "update_scope": "the current update scope",
        "value_case": "the value case",
        "weak_areas": "the weak areas",
    }
    return fallback_map.get(field_name, "the relevant detail")


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _estimate_prompt_tokens(text: str) -> int:
    compact = " ".join(text.split())
    if not compact:
        return 0
    return max(1, int(len(compact.split()) * 1.35))


def _combine_notes(existing: str, addition: str) -> str:
    existing = existing.strip()
    addition = addition.strip()
    if not existing:
        return addition
    if not addition:
        return existing
    return f"{existing}\n\n{addition}"


def _recommended_template_id(inspection) -> str:
    if not inspection or not inspection.recommendations:
        return ""
    return inspection.recommendations[0].get("template_id", "")


def _find_template(template_id: str) -> dict[str, Any] | None:
    for pack in PACK_CATALOG:
        for template in pack["templates"]:
            if template["id"] == template_id:
                return {
                    "id": template["id"],
                    "title": template["title"],
                    "subcategory": template["subcategory"],
                    "summary": template["summary"],
                    "prompt_text": template["prompt_text"],
                    "template_fields": list(template.get("template_fields", [])),
                    "why_it_works": list(template.get("why_it_works", [])),
                    "repair_hints": list(pack.get("repair_hints", [])),
                    "pack": pack["pack"],
                    "category": pack["category"],
                }
    return None


def _remote_prompt_from_form(assistant, form: dict[str, str]):
    raw_index = form.get("remote_index", "").strip()
    if not raw_index.isdigit():
        return None
    index = int(raw_index)
    prompts = assistant.library.cached_remote_prompts()
    if index < 0 or index >= len(prompts):
        return None
    return prompts[index]


def _compact_preview(text: str, limit: int = 140) -> str:
    compact = " ".join((text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _find_open_port(preferred: int | None = None) -> int:
    if preferred is not None:
        with socket() as probe:
            try:
                probe.bind(("127.0.0.1", preferred))
            except OSError:
                pass
            else:
                return preferred

    with socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _write_current_launch_url(assistant, url: str) -> None:
    assistant.settings.ensure_app_home()
    current_url_path = assistant.settings.app_home / "current_url.txt"
    current_url_path.write_text(url, encoding="utf-8")


def _escape(text: Any) -> str:
    return html.escape("" if text is None else str(text))


def _escape_attr(text: Any) -> str:
    return html.escape("" if text is None else str(text), quote=True)
