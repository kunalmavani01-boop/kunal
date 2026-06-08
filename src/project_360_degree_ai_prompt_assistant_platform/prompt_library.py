"""Local and optional web-backed prompt library support."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from io import StringIO
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings
from project_360_degree_ai_prompt_assistant_platform.pack_catalog import PACK_CATALOG


REMOTE_PROMPTS_URL = "https://raw.githubusercontent.com/f/prompts.chat/main/prompts.csv"

INTENT_PROFILES = {
    "business_strategy": {
        "keywords": {
            "business",
            "startup",
            "product",
            "platform",
            "website",
            "market",
            "audience",
            "mvp",
            "strategy",
            "roadmap",
            "opportunity",
            "gap",
            "feature",
            "validate",
            "competitive",
            "competitor",
            "founder",
            "user",
            "users",
            "job",
            "jobs",
        },
        "preferred_packs": {
            "Product Strategy Pack",
            "Business Idea Validation Pack",
            "Proposal Pack",
            "Meeting Summary Pack",
            "General Prompt Repair Pack",
        },
        "avoid_packs": {"Blog Outline Pack", "Email Writing Pack"},
    },
    "writing_content": {
        "keywords": {
            "blog",
            "article",
            "seo",
            "newsletter",
            "copy",
            "headline",
            "post",
            "email",
            "outreach",
            "subject",
        },
        "preferred_packs": {"Blog Outline Pack", "Email Writing Pack", "General Prompt Repair Pack"},
        "avoid_packs": set(),
    },
    "coding_technical": {
        "keywords": {
            "code",
            "bug",
            "error",
            "debug",
            "traceback",
            "function",
            "api",
            "python",
            "javascript",
            "regex",
            "architecture",
        },
        "preferred_packs": {"Code Explainer Pack", "Bug Fix Pack", "General Prompt Repair Pack"},
        "avoid_packs": set(),
    },
    "learning_research": {
        "keywords": {
            "research",
            "study",
            "paper",
            "analysis",
            "analyst",
            "industry",
            "report",
            "findings",
            "summary",
            "evidence",
        },
        "preferred_packs": {"Paper Summary Pack", "Study Guide Pack", "Business Idea Validation Pack"},
        "avoid_packs": {"Email Writing Pack"},
    },
    "creative_story": {
        "keywords": {
            "story",
            "screenplay",
            "script",
            "scene",
            "character",
            "plot",
            "dialogue",
            "creative",
            "fiction",
            "writer",
            "director",
        },
        "preferred_packs": {"Story Idea Pack", "General Prompt Repair Pack"},
        "avoid_packs": {"Blog Outline Pack", "Email Writing Pack"},
    },
}

LIBRARY_CATEGORY_RULES = {
    "mvp_building": {
        "keywords": {"mvp", "scope", "launch", "first release", "v1", "ship", "feature set"},
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack"},
        "subcategories": {"MVP Planning", "Launch Scope", "Feature Prioritization"},
    },
    "product_strategy": {
        "keywords": {"product strategy", "positioning", "roadmap", "product brief", "prioritization", "value prop"},
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack", "Proposal Pack"},
        "subcategories": {"Product Strategy", "Positioning", "Feature Prioritization"},
    },
    "validation_research": {
        "keywords": {"validation", "research", "interview", "market gap", "market research", "competitive", "persona"},
        "packs": {"Business Idea Validation Pack", "Paper Summary Pack", "Meeting Summary Pack"},
        "subcategories": {"Idea Validation", "Gap Analysis", "Research Briefs", "User Research"},
    },
    "website_landing_pages": {
        "keywords": {"website", "landing page", "homepage", "wireframe", "hero section", "site map"},
        "packs": {"Product Strategy Pack", "Proposal Pack", "Blog Outline Pack"},
        "subcategories": {"Landing Pages", "Website Messaging", "Homepage Structure"},
    },
    "messaging_positioning": {
        "keywords": {"messaging", "positioning", "value proposition", "headline", "angle", "differentiator"},
        "packs": {"Product Strategy Pack", "Blog Outline Pack", "Proposal Pack"},
        "subcategories": {"Positioning", "Website Messaging", "Thought Leadership"},
    },
    "sales_outreach": {
        "keywords": {"sales", "outreach", "cold email", "follow-up", "prospect", "reply", "lead"},
        "packs": {"Email Writing Pack", "Proposal Pack"},
        "subcategories": {"Cold Outreach", "Sales Emails", "Follow-ups"},
    },
    "proposals_client_work": {
        "keywords": {"proposal", "client", "scope", "statement of work", "pricing", "deliverables"},
        "packs": {"Proposal Pack", "Meeting Summary Pack"},
        "subcategories": {"Client Proposals", "Scoping", "Service Packaging"},
    },
    "content_seo": {
        "keywords": {"seo", "blog", "content", "article", "outline", "search intent", "keyword"},
        "packs": {"Blog Outline Pack"},
        "subcategories": {"SEO Outlines", "Content Briefs", "Thought Leadership"},
    },
    "social_creator": {
        "keywords": {"social", "creator", "twitter", "linkedin post", "thread", "instagram", "youtube"},
        "packs": {"Blog Outline Pack", "Email Writing Pack", "General Prompt Repair Pack"},
        "subcategories": {"Social Posts", "Thread Ideas", "Creator Hooks"},
    },
    "study_learning": {
        "keywords": {"study", "learning", "exam", "revision", "student", "teacher", "lesson"},
        "packs": {"Study Guide Pack", "Paper Summary Pack"},
        "subcategories": {"Study Guides", "Lesson Support", "Revision Plans"},
    },
    "research_summaries": {
        "keywords": {"summary", "paper", "research summary", "abstract", "literature", "findings"},
        "packs": {"Paper Summary Pack", "Study Guide Pack"},
        "subcategories": {"Accessible Summaries", "Research Briefs"},
    },
    "coding_help": {
        "keywords": {"code", "developer", "function", "terminal", "refactor", "explain code", "programming"},
        "packs": {"Code Explainer Pack"},
        "subcategories": {"Beginner Explainers", "Code Walkthroughs", "Developer Guidance"},
    },
    "debugging_fixes": {
        "keywords": {"debug", "bug", "error", "traceback", "fix", "broken", "reproduce"},
        "packs": {"Bug Fix Pack", "Code Explainer Pack"},
        "subcategories": {"Root Cause Analysis", "Bug Reproduction", "Fix Plans"},
    },
    "apis_architecture": {
        "keywords": {"api", "architecture", "system design", "microservice", "database", "integration"},
        "packs": {"Code Explainer Pack", "Bug Fix Pack"},
        "subcategories": {"APIs", "Architecture", "Integration Planning"},
    },
    "story_screenplay": {
        "keywords": {"story", "screenplay", "script", "plot", "writer", "director", "narrative"},
        "packs": {"Story Idea Pack"},
        "subcategories": {"Story Outlines", "Screenplay Development", "Narrative Planning"},
    },
    "character_scene": {
        "keywords": {"character", "scene", "dialogue", "character arc", "scene beat", "protagonist"},
        "packs": {"Story Idea Pack"},
        "subcategories": {"Character Design", "Scene Writing", "Dialogue"},
    },
    "productivity_planning": {
        "keywords": {"planning", "weekly", "productivity", "habit", "task list", "calendar", "priorities"},
        "packs": {"Meeting Summary Pack", "General Prompt Repair Pack"},
        "subcategories": {"Planning", "Weekly Planning", "Prioritization"},
    },
    "decision_making": {
        "keywords": {"decision", "trade-off", "choose", "comparison", "decision memo", "pros and cons"},
        "packs": {"Product Strategy Pack", "Business Idea Validation Pack", "Meeting Summary Pack"},
        "subcategories": {"Decision Support", "Comparisons", "Trade-offs"},
    },
    "prompt_repair": {
        "keywords": {"prompt", "rewrite", "refine", "clarify", "improve prompt", "prompt fix"},
        "packs": {"General Prompt Repair Pack"},
        "subcategories": {"Prompt Repair"},
    },
    "general_use": {
        "keywords": {"general", "assistant", "help me", "act as", "useful response"},
        "packs": {"General Prompt Repair Pack"},
        "subcategories": {"Prompt Repair", "General Use"},
    },
}


@dataclass
class LibraryPrompt:
    title: str
    pack: str
    subcategory: str
    domain: str
    interest: str
    summary: str
    prompt_text: str
    source_label: str
    source_url: str
    origin: str
    template_fields: list[str] = field(default_factory=list)
    common_missing_elements: list[str] = field(default_factory=list)
    repair_hints: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    why_it_works: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PromptRecommendation:
    template_id: str
    title: str
    pack: str
    subcategory: str
    category: str
    summary: str
    score: int
    reason: str
    template_fields: list[str]
    common_missing_elements: list[str]
    repair_hints: list[str]
    prompt_text: str

    def to_dict(self) -> dict:
        return asdict(self)


class PromptLibrary:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.settings.ensure_app_home()
        self.cache_path = self.settings.app_home / "prompt_library_cache.json"
        self.seed_path = Path(__file__).resolve().parent / "data" / "open_source_prompt_seed.json"

    def search(
        self,
        *,
        query: str = "",
        category: str = "All",
        pack: str = "All",
        subcategory: str = "All",
        domain: str = "All",
        interest: str = "All",
    ) -> list[LibraryPrompt]:
        prompts = self.local_prompts() + self.cached_remote_prompts()
        query_lower = query.strip().lower()
        results: list[LibraryPrompt] = []
        for prompt in prompts:
            if category != "All" and pack_category(prompt.pack) != category:
                continue
            if pack != "All" and prompt.pack != pack:
                continue
            if subcategory != "All" and prompt.subcategory != subcategory:
                continue
            if domain != "All" and prompt.domain != domain:
                continue
            if interest != "All" and prompt.interest != interest:
                continue
            haystack = " ".join(
                [
                    prompt.title,
                    pack_category(prompt.pack),
                    prompt.pack,
                    prompt.subcategory,
                    prompt.summary,
                    prompt.prompt_text,
                    prompt.domain,
                    prompt.interest,
                ]
            ).lower()
            if query_lower and query_lower not in haystack:
                continue
            results.append(prompt)
        return results

    def available_categories(self) -> list[str]:
        values = sorted({pack_category(prompt.pack) for prompt in self.local_prompts() + self.cached_remote_prompts()})
        return ["All", *values]

    def available_packs(self, category: str = "All") -> list[str]:
        prompts = self.local_prompts() + self.cached_remote_prompts()
        if category != "All":
            prompts = [prompt for prompt in prompts if pack_category(prompt.pack) == category]
        values = sorted({prompt.pack for prompt in prompts})
        return ["All", *values]

    def available_subcategories(self, pack: str = "All", category: str = "All") -> list[str]:
        prompts = self.local_prompts() + self.cached_remote_prompts()
        if category != "All":
            prompts = [prompt for prompt in prompts if pack_category(prompt.pack) == category]
        if pack != "All":
            prompts = [prompt for prompt in prompts if prompt.pack == pack]
        values = sorted({prompt.subcategory for prompt in prompts})
        return ["All", *values]

    def available_domains(self) -> list[str]:
        values = sorted({prompt.domain for prompt in self.local_prompts() + self.cached_remote_prompts()})
        return ["All", *values]

    def available_interests(self) -> list[str]:
        values = sorted({prompt.interest for prompt in self.local_prompts() + self.cached_remote_prompts()})
        return ["All", *values]

    def category_for_pack(self, pack: str) -> str:
        return pack_category(pack)

    def recommend(self, prompt: str, limit: int = 3) -> list[PromptRecommendation]:
        prompt_lower = prompt.lower()
        query_terms = {term for term in _search_terms(prompt) if len(term) >= 4}
        if not query_terms:
            return []

        intent = classify_prompt_intent(prompt)
        scored: list[tuple[float, LibraryPrompt]] = []
        for candidate in self.local_prompts():
            candidate_blob = " ".join(
                [
                    candidate.title,
                    candidate.summary,
                    candidate.prompt_text,
                    " ".join(candidate.keywords),
                    candidate.pack,
                    candidate.subcategory,
                    pack_category(candidate.pack),
                ]
            )
            candidate_terms = {term for term in _search_terms(candidate_blob) if len(term) >= 4}
            overlap_terms = query_terms & candidate_terms
            overlap = len(overlap_terms)

            score = overlap * 1.8
            if candidate.origin == "local":
                score += 0.8
            if candidate.pack in prompt or candidate.subcategory.lower() in prompt_lower:
                score += 0.7
            if candidate.pack in intent["preferred_packs"]:
                score += 2.4
            if candidate.pack in intent["avoid_packs"]:
                score -= 2.2
            if intent["category"] == pack_category(candidate.pack):
                score += 1.6
            if any(phrase in prompt_lower for phrase in candidate.keywords if len(phrase.split()) > 1):
                score += 1.0
            if any(word in prompt_lower for word in candidate.template_fields):
                score += 0.6
            if overlap == 0 and candidate.pack != "General Prompt Repair Pack":
                if candidate.pack not in intent["preferred_packs"]:
                    continue
                score -= 1.0
            if _looks_like_wrong_lane(prompt_lower, candidate.pack):
                score -= 3.0
            if score <= 0:
                continue
            scored.append((score, candidate))

        scored.sort(key=lambda item: item[0], reverse=True)
        if not scored:
            fallback = self.search(pack="General Prompt Repair Pack")
            scored = [(1.0, fallback[0])] if fallback else []

        recommendations: list[PromptRecommendation] = []
        top_score = scored[0][0] if scored else 1.0
        for raw_score, candidate in scored[:limit]:
            candidate_terms = {
                term
                for term in _search_terms(
                    " ".join([candidate.title, candidate.summary, candidate.prompt_text, " ".join(candidate.keywords)])
                )
            }
            matched_terms = sorted(query_terms & candidate_terms)
            reason = _recommendation_reason(candidate, matched_terms, intent)
            recommendations.append(
                PromptRecommendation(
                    template_id=_template_id_for_candidate(candidate),
                    title=candidate.title,
                    pack=candidate.pack,
                    subcategory=candidate.subcategory,
                    category=pack_category(candidate.pack),
                    summary=candidate.summary,
                    score=max(55, min(97, int(55 + (raw_score / max(top_score, 1.0)) * 40))),
                    reason=reason,
                    template_fields=list(candidate.template_fields),
                    common_missing_elements=list(candidate.common_missing_elements),
                    repair_hints=list(candidate.repair_hints),
                    prompt_text=candidate.prompt_text,
                )
            )
        return recommendations

    def refresh_remote_prompts(self, limit: int = 80) -> int:
        try:
            with urlopen(REMOTE_PROMPTS_URL, timeout=20) as response:
                raw_text = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"Could not refresh the open-source prompt library: {exc.reason}") from exc

        reader = csv.DictReader(StringIO(raw_text))
        prompts: list[dict] = []
        for row in reader:
            title = (row.get("act") or "").strip()
            prompt_text = (row.get("prompt") or "").strip()
            if not title or not prompt_text:
                continue
            domain = infer_domain(title, prompt_text)
            interest = infer_interest(title, prompt_text)
            prompts.append(
                LibraryPrompt(
                    title=title,
                    pack=infer_pack(title, prompt_text),
                    subcategory=infer_subcategory(title, prompt_text),
                    domain=domain,
                    interest=interest,
                    summary=first_sentence(prompt_text),
                    prompt_text=prompt_text,
                    source_label="prompts.chat",
                    source_url=REMOTE_PROMPTS_URL,
                    origin="remote",
                ).to_dict()
            )
            if len(prompts) >= limit:
                break

        self.cache_path.write_text(json.dumps(prompts, indent=2), encoding="utf-8")
        return len(prompts)

    def local_prompts(self) -> list[LibraryPrompt]:
        prompts: list[LibraryPrompt] = []
        for pack in PACK_CATALOG:
            for template in pack["templates"]:
                prompts.append(
                    LibraryPrompt(
                        title=template["title"],
                        pack=pack["pack"],
                        subcategory=template["subcategory"],
                        domain=pack["domain"],
                        interest=pack["interest"],
                        summary=template["summary"],
                        prompt_text=template["prompt_text"],
                        source_label="Built-in Pack",
                        source_url="local",
                        origin="local",
                        template_fields=list(template.get("template_fields", [])),
                        common_missing_elements=list(pack.get("common_missing_elements", [])),
                        repair_hints=list(pack.get("repair_hints", [])),
                        keywords=list(pack.get("keywords", [])) + list(template.get("keywords", [])),
                        why_it_works=list(template.get("why_it_works", [])),
                    )
                )
        return prompts

    def cached_remote_prompts(self) -> list[LibraryPrompt]:
        prompts: list[LibraryPrompt] = []
        seen: set[tuple[str, str]] = set()
        for prompt in self._read_remote_prompt_file(self.seed_path) + self._read_remote_prompt_file(self.cache_path):
            key = (prompt.title.strip().lower(), prompt.prompt_text.strip().lower())
            if key in seen:
                continue
            seen.add(key)
            prompts.append(prompt)
        return prompts

    def _read_remote_prompt_file(self, path: Path) -> list[LibraryPrompt]:
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

        prompts: list[LibraryPrompt] = []
        for item in raw:
            title = (item.get("title") or "").strip()
            prompt_text = (item.get("prompt_text") or "").strip()
            if not title or not prompt_text:
                continue

            normalized = dict(item)
            normalized.setdefault("pack", infer_pack(title, prompt_text))
            normalized.setdefault("subcategory", infer_subcategory(title, prompt_text))
            normalized.setdefault("domain", infer_domain(title, prompt_text))
            normalized.setdefault("interest", infer_interest(title, prompt_text))
            normalized.setdefault("summary", first_sentence(prompt_text))
            normalized.setdefault("source_label", "Open Source")
            normalized.setdefault("source_url", "local")
            normalized.setdefault("origin", "remote")
            normalized.setdefault("template_fields", [])
            normalized.setdefault("common_missing_elements", [])
            normalized.setdefault("repair_hints", [])
            normalized.setdefault("keywords", [])
            normalized.setdefault("why_it_works", [])
            prompts.append(LibraryPrompt(**normalized))
        return prompts


def _template_id_for_candidate(candidate: LibraryPrompt) -> str:
    for pack in PACK_CATALOG:
        if pack["pack"] != candidate.pack:
            continue
        for template in pack["templates"]:
            if template["title"] == candidate.title and template["subcategory"] == candidate.subcategory:
                return template["id"]
    return ""


def pack_category(pack: str) -> str:
    mapping = {
        "Blog Outline Pack": "Writing & Content",
        "Email Writing Pack": "Writing & Content",
        "Product Strategy Pack": "Business & Strategy",
        "Business Idea Validation Pack": "Business & Strategy",
        "Proposal Pack": "Business & Strategy",
        "Meeting Summary Pack": "Business & Strategy",
        "Code Explainer Pack": "Coding & Technical",
        "Bug Fix Pack": "Coding & Technical",
        "Study Guide Pack": "Learning & Research",
        "Paper Summary Pack": "Learning & Research",
        "Story Idea Pack": "Creative & General",
        "General Prompt Repair Pack": "Creative & General",
    }
    return mapping.get(pack, "Creative & General")


def infer_domain(title: str, prompt_text: str) -> str:
    haystack = f"{title} {prompt_text}".lower()
    if any(word in haystack for word in ["startup", "market gap", "platform", "product strategy", "mvp", "founder", "positioning", "proposal", "client"]):
        return "Business"
    if any(word in haystack for word in ["website", "landing page", "homepage", "headline", "hero section"]):
        return "Business"
    if any(word in haystack for word in ["developer", "terminal", "javascript", "python", "code", "regex"]):
        return "Coding"
    if any(word in haystack for word in ["api", "architecture", "system design", "database", "integration"]):
        return "Coding"
    if any(word in haystack for word in ["story", "character", "scene", "creative writing", "fiction"]):
        return "Creative"
    if any(word in haystack for word in ["advertiser", "blog", "marketing", "campaign", "copy", "email", "seo", "social", "thread", "linkedin"]):
        return "Marketing"
    if any(word in haystack for word in ["teacher", "study", "tutor", "education", "student", "paper"]):
        return "Education"
    if any(word in haystack for word in ["weekly planning", "productivity", "habit", "priorities", "decision"]):
        return "Productivity"
    if any(word in haystack for word in ["proposal", "meeting", "stakeholder", "strategy", "client"]):
        return "Business"
    return "General"


def infer_interest(title: str, prompt_text: str) -> str:
    haystack = f"{title} {prompt_text}".lower()
    if any(word in haystack for word in ["startup", "founder", "product", "market", "strategy"]):
        return "Founders"
    if "email" in haystack or "outreach" in haystack or "blog" in haystack or "seo" in haystack:
        return "Outreach"
    if "proposal" in haystack or "meeting" in haystack or "stakeholder" in haystack:
        return "Operators"
    if "teacher" in haystack or "student" in haystack or "study" in haystack or "paper" in haystack:
        return "Learning"
    if "developer" in haystack or "code" in haystack or "terminal" in haystack or "bug" in haystack:
        return "Builders"
    if "story" in haystack or "character" in haystack or "creative" in haystack:
        return "Creators"
    if "productivity" in haystack or "planning" in haystack or "habit" in haystack:
        return "Productivity"
    return "General"


def infer_pack(title: str, prompt_text: str) -> str:
    haystack = f"{title} {prompt_text}".lower()
    if any(word in haystack for word in ["startup", "platform", "product strategy", "mvp", "feature priority", "positioning", "roadmap", "value proposition"]):
        return "Product Strategy Pack"
    if any(word in haystack for word in ["market gap", "validate", "business idea", "opportunity", "founder research", "user interview", "persona", "discovery"]):
        return "Business Idea Validation Pack"
    if any(word in haystack for word in ["blog", "article", "newsletter", "seo outline", "landing page copy", "headline", "homepage"]):
        return "Blog Outline Pack"
    if any(word in haystack for word in ["email", "outreach", "follow-up", "launch email", "cold email", "subject line"]):
        return "Email Writing Pack"
    if any(word in haystack for word in ["proposal", "statement of work", "pricing proposal", "scope doc", "client brief"]):
        return "Proposal Pack"
    if any(word in haystack for word in ["meeting", "notes", "recap", "standup", "weekly planning", "action items", "decision memo"]):
        return "Meeting Summary Pack"
    if any(word in haystack for word in ["bug", "error", "traceback", "fix", "reproduce", "broken"]):
        return "Bug Fix Pack"
    if any(word in haystack for word in ["code", "function", "regex", "architecture", "api", "integration", "system design", "terminal"]):
        return "Code Explainer Pack"
    if any(word in haystack for word in ["paper", "research", "abstract", "literature review", "findings", "industry overview"]):
        return "Paper Summary Pack"
    if any(word in haystack for word in ["study", "exam", "concept", "revision", "lesson", "learn faster"]):
        return "Study Guide Pack"
    if any(word in haystack for word in ["story", "character", "scene", "fiction", "dialogue", "screenplay", "script"]):
        return "Story Idea Pack"
    return "General Prompt Repair Pack"


def infer_subcategory(title: str, prompt_text: str) -> str:
    haystack = f"{title} {prompt_text}".lower()
    if any(word in haystack for word in ["product strategy", "positioning", "feature priority"]):
        return "Product Strategy"
    if any(word in haystack for word in ["mvp", "launch scope"]):
        return "MVP Planning"
    if any(word in haystack for word in ["feature priority", "priority matrix", "prioritization"]):
        return "Feature Prioritization"
    if any(word in haystack for word in ["market gap", "opportunity"]):
        return "Gap Analysis"
    if any(word in haystack for word in ["validate", "business idea", "problem interview", "user research"]):
        return "Idea Validation"
    if any(word in haystack for word in ["landing page", "homepage", "website copy", "wireframe"]):
        return "Landing Pages"
    if any(word in haystack for word in ["messaging", "headline", "value proposition", "positioning angle"]):
        return "Website Messaging"
    if any(word in haystack for word in ["email", "outreach", "follow-up"]):
        return "Cold Outreach"
    if any(word in haystack for word in ["sales email", "subject line", "prospect"]):
        return "Sales Emails"
    if any(word in haystack for word in ["newsletter"]):
        return "Newsletter Drafts"
    if any(word in haystack for word in ["blog", "seo", "article"]):
        return "SEO Outlines"
    if any(word in haystack for word in ["social", "thread", "linkedin post", "twitter thread"]):
        return "Social Posts"
    if any(word in haystack for word in ["proposal", "pricing proposal", "statement of work"]):
        return "Client Proposals"
    if any(word in haystack for word in ["scope doc", "deliverables", "pricing", "retainer"]):
        return "Scoping"
    if any(word in haystack for word in ["meeting", "standup", "recap"]):
        return "Executive Summaries"
    if any(word in haystack for word in ["weekly planning", "weekly plan", "priorities", "habits"]):
        return "Weekly Planning"
    if any(word in haystack for word in ["decision memo", "trade-off", "pros and cons", "comparison"]):
        return "Decision Support"
    if any(word in haystack for word in ["study", "student", "guide", "revision"]):
        return "Study Guides"
    if any(word in haystack for word in ["lesson", "teacher", "tutor"]):
        return "Lesson Support"
    if any(word in haystack for word in ["paper", "abstract", "research"]):
        return "Accessible Summaries"
    if any(word in haystack for word in ["research brief", "industry overview", "findings"]):
        return "Research Briefs"
    if any(word in haystack for word in ["bug", "error", "fix", "traceback"]):
        return "Root Cause Analysis"
    if any(word in haystack for word in ["reproduce", "bug reproduction"]):
        return "Bug Reproduction"
    if any(word in haystack for word in ["api", "endpoint", "rest api"]):
        return "APIs"
    if any(word in haystack for word in ["architecture", "system design", "database", "integration"]):
        return "Architecture"
    if any(word in haystack for word in ["code", "function", "regex", "terminal"]):
        return "Beginner Explainers"
    if any(word in haystack for word in ["dialogue", "character arc", "protagonist"]):
        return "Character Design"
    if any(word in haystack for word in ["scene beat", "scene", "script scene"]):
        return "Scene Writing"
    if any(word in haystack for word in ["story", "fiction", "plot", "outline", "screenplay"]):
        return "Story Outlines"
    if any(word in haystack for word in ["prompt", "rewrite", "refine", "improve prompt"]):
        return "Prompt Repair"
    return "Prompt Repair"


def classify_library_flow_ids(
    *,
    title: str,
    prompt_text: str,
    pack: str = "",
    subcategory: str = "",
    domain: str = "",
    interest: str = "",
) -> set[str]:
    haystack = " ".join([title, prompt_text, pack, subcategory, domain, interest]).lower()
    matched: set[str] = set()
    for flow_id, rule in LIBRARY_CATEGORY_RULES.items():
        if pack and pack in rule["packs"]:
            matched.add(flow_id)
            continue
        if subcategory and subcategory in rule["subcategories"]:
            matched.add(flow_id)
            continue
        if any(keyword in haystack for keyword in rule["keywords"]):
            matched.add(flow_id)
    if not matched:
        matched.add("general_use")
    if matched == {"prompt_repair", "general_use"}:
        return {"general_use"}
    return matched


def first_sentence(text: str) -> str:
    compact = " ".join(text.split())
    sentence = compact.split(".")[0].strip()
    if len(sentence) > 120:
        return sentence[:117].rstrip() + "..."
    return sentence or compact[:120]


def _search_terms(text: str) -> list[str]:
    return [term.lower() for term in re.findall(r"[a-zA-Z0-9']+", text)]


def classify_prompt_intent(prompt: str) -> dict[str, object]:
    prompt_terms = set(_search_terms(prompt))
    prompt_lower = prompt.lower()

    best_name = "creative_story"
    best_score = -1
    for name, profile in INTENT_PROFILES.items():
        score = len(prompt_terms & profile["keywords"])
        if any(phrase in prompt_lower for phrase in profile["keywords"] if " " in phrase):
            score += 2
        if score > best_score:
            best_name = name
            best_score = score

    category_by_name = {
        "business_strategy": "Business & Strategy",
        "writing_content": "Writing & Content",
        "coding_technical": "Coding & Technical",
        "learning_research": "Learning & Research",
        "creative_story": "Creative & General",
    }
    profile = INTENT_PROFILES[best_name]
    return {
        "name": best_name,
        "category": category_by_name[best_name],
        "preferred_packs": profile["preferred_packs"],
        "avoid_packs": profile["avoid_packs"],
    }


def _looks_like_wrong_lane(prompt_lower: str, pack: str) -> bool:
    business_words = ("product", "platform", "startup", "website", "market", "mvp", "feature", "business")
    content_words = ("blog", "seo", "newsletter", "article", "email", "subject line")
    story_words = ("screenplay", "script", "scene", "character", "writer", "director")

    if pack in {"Blog Outline Pack", "Email Writing Pack"} and any(word in prompt_lower for word in business_words):
        if not any(word in prompt_lower for word in content_words):
            return True
    if pack in {"Blog Outline Pack", "Email Writing Pack"} and any(word in prompt_lower for word in story_words):
        return True
    if pack == "Story Idea Pack" and any(word in prompt_lower for word in business_words):
        return True
    return False


def _recommendation_reason(candidate: LibraryPrompt, matched_terms: list[str], intent: dict[str, object]) -> str:
    if candidate.pack in intent["preferred_packs"]:
        if matched_terms:
            return f"Best fit for this intent; matched on: {', '.join(matched_terms[:4])}"
        return "Best fit for the kind of result your prompt seems to need."
    if matched_terms:
        return f"Matched on: {', '.join(matched_terms[:4])}"
    return "Matched the structure this prompt is likely to need."
