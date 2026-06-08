"""Prompt analysis and rewrite helpers."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable


ACTION_WORDS = {
    "analyze",
    "build",
    "create",
    "compare",
    "debug",
    "design",
    "draft",
    "explain",
    "generate",
    "improve",
    "outline",
    "plan",
    "review",
    "rewrite",
    "summarize",
    "write",
}
CONTEXT_HINTS = {"for", "because", "background", "context", "audience", "company", "product"}
OUTPUT_HINTS = {"table", "json", "bullet", "email", "essay", "summary", "format", "markdown"}
CONSTRAINT_HINTS = {"must", "should", "avoid", "limit", "under", "maximum", "minimum", "only"}
EXAMPLE_HINTS = {"example", "sample", "like", "such as"}
SECTION_HEADINGS = {
    "task:",
    "context files:",
    "reference:",
    "reference patterns to reuse:",
    "success brief:",
    "rules:",
    "conversation:",
    "plan:",
    "alignment:",
}


@dataclass
class PromptAnalysis:
    score: int
    strengths: list[str]
    gaps: list[str]
    suggestions: list[str]
    keywords: list[str]
    recommended_sections: list[str]
    subscores: dict[str, int]
    risk_flags: list[str]
    health_label: str
    repair_mode: bool

    def to_dict(self) -> dict:
        return asdict(self)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def analyze_prompt(
    prompt: str,
    extra_context: str = "",
    output_format: str = "",
    constraints: Iterable[str] | None = None,
) -> PromptAnalysis:
    cleaned_prompt = " ".join(prompt.split())
    words = tokenize(cleaned_prompt)
    constraints = [item.strip() for item in (constraints or []) if item.strip()]

    strengths: list[str] = []
    gaps: list[str] = []
    suggestions: list[str] = []
    risk_flags: list[str] = []

    if len(words) >= 8:
        strengths.append("The prompt contains enough surface detail to work with.")
    else:
        gaps.append("The request is too short and leaves room for guesswork.")
        suggestions.append("State the task in one complete sentence before adding details.")
        risk_flags.append("High ambiguity risk from very short input.")

    if any(word in ACTION_WORDS for word in words[:12]):
        strengths.append("The task direction is reasonably clear.")
    else:
        gaps.append("The main action is not explicit.")
        suggestions.append("Start with a direct verb such as write, analyze, compare, or build.")

    if extra_context or any(word in CONTEXT_HINTS for word in words):
        strengths.append("There is some context that helps the model understand the situation.")
    else:
        gaps.append("The prompt lacks background or audience context.")
        suggestions.append("Add who this is for, why it matters, and what situation the model should assume.")
        risk_flags.append("Missing context increases hallucination risk.")

    if output_format or any(word in OUTPUT_HINTS for word in words):
        strengths.append("The expected output shape is defined or implied.")
    else:
        gaps.append("The desired output format is missing.")
        suggestions.append("Specify whether you want bullets, table, JSON, step-by-step instructions, or another format.")
        risk_flags.append("The model may choose an unhelpful format on its own.")

    if constraints or any(word in CONSTRAINT_HINTS for word in words):
        strengths.append("The prompt includes at least one constraint or quality bar.")
    else:
        gaps.append("There are no constraints to keep the answer focused.")
        suggestions.append("Add limits such as tone, word count, exclusions, or success criteria.")
        risk_flags.append("No constraints means more wasted tokens and drift.")

    if any(word in EXAMPLE_HINTS for word in words):
        strengths.append("The prompt hints at examples or comparisons.")
    else:
        suggestions.append("If possible, include a short example or a reference style to anchor the answer.")
        risk_flags.append("No reference signal means style can drift.")

    section_hits = sum(1 for section in SECTION_HEADINGS if section in cleaned_prompt.lower())
    if section_hits >= 4:
        strengths.append("The prompt uses a clear multi-section structure.")
    else:
        suggestions.append("Use explicit sections such as task, reference, success brief, rules, and plan.")

    if "recipient" in cleaned_prompt.lower() or "audience" in cleaned_prompt.lower():
        strengths.append("The audience is defined.")
    else:
        suggestions.append("Name the audience so the output can match the right depth and tone.")

    if "success means" in cleaned_prompt.lower() or "desired effect" in cleaned_prompt.lower():
        strengths.append("The prompt explains how success will be judged.")
    else:
        suggestions.append("Say what success looks like so the model can optimize for it.")
        risk_flags.append("No success criteria means weak optimization target.")

    filler_phrases = sum(
        cleaned_prompt.lower().count(phrase)
        for phrase in ["please", "kind of", "something like", "maybe", "just", "basically"]
    )
    if filler_phrases >= 3:
        risk_flags.append("The prompt includes filler phrasing that can waste tokens.")

    keyword_candidates = []
    seen = set()
    for word in words:
        if len(word) < 4 or word in seen:
            continue
        seen.add(word)
        keyword_candidates.append(word)
        if len(keyword_candidates) == 8:
            break

    clarity_score = 40
    if len(words) >= 8:
        clarity_score += 18
    if any(word in ACTION_WORDS for word in words[:12]):
        clarity_score += 18
    if len(words) > 40:
        clarity_score += 6
    clarity_score = min(100, clarity_score)

    context_score = 30
    if extra_context or any(word in CONTEXT_HINTS for word in words):
        context_score += 35
    if "recipient" in cleaned_prompt.lower() or "audience" in cleaned_prompt.lower():
        context_score += 20
    if "success means" in cleaned_prompt.lower() or "desired effect" in cleaned_prompt.lower():
        context_score += 15
    context_score = min(100, context_score)

    structure_score = 28
    if output_format or any(word in OUTPUT_HINTS for word in words):
        structure_score += 28
    if constraints or any(word in CONSTRAINT_HINTS for word in words):
        structure_score += 24
    structure_score += min(24, section_hits * 6)
    structure_score = min(100, structure_score)

    grounding_score = 32
    if extra_context:
        grounding_score += 25
    if any(word in EXAMPLE_HINTS for word in words):
        grounding_score += 18
    if section_hits >= 3:
        grounding_score += 10
    if "reference:" in cleaned_prompt.lower():
        grounding_score += 15
    grounding_score = min(100, grounding_score)

    efficiency_score = 72
    efficiency_score -= len(gaps) * 8
    efficiency_score -= min(18, filler_phrases * 4)
    if output_format or any(word in OUTPUT_HINTS for word in words):
        efficiency_score += 8
    if constraints or any(word in CONSTRAINT_HINTS for word in words):
        efficiency_score += 8
    efficiency_score = max(20, min(100, efficiency_score))

    score = int(
        (clarity_score * 0.28)
        + (context_score * 0.22)
        + (structure_score * 0.22)
        + (grounding_score * 0.14)
        + (efficiency_score * 0.14)
    )
    if not gaps:
        score += 4
    score = max(20, min(100, score))
    if score >= 85:
        health_label = "Strong"
    elif score >= 75:
        health_label = "Usable"
    elif score >= 60:
        health_label = "Needs Repair"
    else:
        health_label = "High Risk"

    return PromptAnalysis(
        score=score,
        strengths=strengths,
        gaps=gaps,
        suggestions=suggestions or ["The prompt is already well-structured. Tighten wording only if needed."],
        keywords=keyword_candidates,
        recommended_sections=[
            "Task",
            "Context Files",
            "Reference",
            "Success Brief",
            "Rules",
            "Conversation",
            "Plan",
            "Alignment",
        ],
        subscores={
            "clarity": clarity_score,
            "context": context_score,
            "structure": structure_score,
            "grounding": grounding_score,
            "efficiency": efficiency_score,
        },
        risk_flags=_dedupe_preserve_order(risk_flags)[:5],
        health_label=health_label,
        repair_mode=score < 75,
    )


def build_improved_prompt(
    prompt: str,
    analysis: PromptAnalysis,
    memories: list[dict] | None = None,
    extra_context: str = "",
    output_format: str = "",
    constraints: Iterable[str] | None = None,
    tone: str = "clear and practical",
) -> str:
    constraints = [item.strip() for item in (constraints or []) if item.strip()]
    memories = memories or []
    sections = ["Task:", prompt.strip()]

    context_lines = []
    if extra_context:
        context_lines.append(extra_context.strip())
    if memories:
        context_lines.append("Relevant local memory to reuse:")
        for memory in memories:
            context_lines.append(f"- {memory['prompt_preview']}")
            if memory.get("feedback"):
                context_lines.append(f"  Feedback: {memory['feedback']}")
    if context_lines:
        sections.extend(["", "Context:", *context_lines])

    requirement_lines = [
        f"- Keep the response {tone}.",
        "- Preserve the user's original goal and intent.",
    ]
    for constraint in constraints:
        requirement_lines.append(f"- {constraint}")
    if not constraints:
        requirement_lines.append("- State any assumptions briefly instead of guessing silently.")
    sections.extend(["", "Requirements:", *requirement_lines])

    if output_format:
        sections.extend(["", "Output Format:", output_format.strip()])
    else:
        sections.extend(["", "Output Format:", "Use a structure that is easy to scan and act on."])

    quality_checks = []
    if analysis.gaps:
        quality_checks.extend(f"- Fix: {gap}" for gap in analysis.gaps)
    quality_checks.extend(f"- Aim for: {item}" for item in analysis.strengths[:3])
    quality_checks.extend(f"- Improve with: {item}" for item in analysis.suggestions[:3])
    sections.extend(["", "Quality Checks:", *quality_checks])

    return "\n".join(sections).strip()


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
