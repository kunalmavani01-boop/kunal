"""Guided prompt intake and structured prompt builder."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

TASK_TYPE_HINTS = {
    "email": [
        "Name the recipient so the tone and detail level fit the person reading it.",
        "Say what action you want after the email is read.",
        "Add a word limit so the email stays focused.",
    ],
    "landing page": [
        "Name the audience and the one action the page should drive.",
        "State what proof or credibility signals should appear early.",
        "Clarify what tone to avoid so it does not sound generic.",
    ],
    "proposal": [
        "Say what decision you want the proposal to unlock.",
        "Name the audience and the level of detail they need.",
        "Add the format sections you want included.",
    ],
    "post": [
        "Say which platform this is for so the style matches the channel.",
        "Clarify the reaction or engagement you want.",
        "Set a tone or voice so it does not feel generic.",
    ],
    "ad": [
        "Name the audience and the offer clearly.",
        "Say what the reader should do after seeing it.",
        "Add channel or length constraints so the copy stays tight.",
    ],
}


@dataclass
class GuidedPromptBlueprint:
    task: str
    goal: str = ""
    context_files: list[str] = field(default_factory=list)
    reference_text: str = ""
    reference_patterns: list[str] = field(default_factory=list)
    output_type: str = ""
    recipient: str = ""
    desired_action: str = ""
    avoid: str = ""
    success_criteria: str = ""
    rules: list[str] = field(default_factory=list)
    tone: str = "clear and practical"

    def to_dict(self) -> dict:
        return asdict(self)


def collect_guided_blueprint(args) -> GuidedPromptBlueprint:
    task = _ensure_value(
        getattr(args, "task", "") or "",
        "Start with your rough one-line prompt. What do you want the model to do?",
    )
    ideas = suggest_prompt_upgrades(task)
    if ideas:
        print("\nQuick ideas to strengthen this prompt:")
        for item in ideas:
            print(f"- {item}")

    goal = _ask_optional(
        getattr(args, "goal", "") or "",
        "What should success look like after the answer? Press Enter to let the assistant infer it.",
    )
    output_type = _ask_optional(
        getattr(args, "output_type", "") or "",
        "What type of output do you want? Example: email, memo, landing page, proposal. Press Enter to let the assistant choose.",
    )
    recipient = _ask_optional(
        getattr(args, "recipient", "") or "",
        "Who is the audience or recipient? Press Enter to skip.",
    )
    desired_action = _ask_optional(
        getattr(args, "desired_action", "") or "",
        "After reading, what should they think, feel, or do? Press Enter to skip.",
    )
    avoid = _ask_optional(
        getattr(args, "avoid", "") or "",
        "Optional: what should the answer avoid sounding like?",
    )
    success_criteria = _ask_optional(
        getattr(args, "success", "") or "",
        "How will you judge whether the answer worked? Press Enter to skip.",
    )
    rules = _collect_repeating_optional(
        list(getattr(args, "rule", []) or []),
        "Optional: list any hard rules, constraints, or landmines. Press Enter on a blank line when done.",
        "Rule",
    )
    wants_deep_setup = _should_collect_deep_context(args)
    context_files: list[str] = []
    reference_text = ""
    reference_patterns: list[str] = []
    if wants_deep_setup:
        context_files = _collect_repeating_optional(
            list(getattr(args, "context_file", []) or []),
            "Add any context files to read first. Press Enter on a blank line when done.",
            "Context file",
        )
        reference_text = _ask_optional(
            getattr(args, "reference", "") or "",
            "Do you have a reference, example, or inspiration to emulate?",
        )
        reference_patterns = _collect_repeating_optional(
            list(getattr(args, "reference_pattern", []) or []),
            "List the patterns or qualities that make the reference strong. Press Enter on a blank line when done.",
            "Reference pattern",
        )
    tone = _ask_optional(
        getattr(args, "tone", "") or "clear and practical",
        "Preferred tone",
    ) or "clear and practical"

    return GuidedPromptBlueprint(
        task=task,
        goal=goal,
        context_files=context_files,
        reference_text=reference_text,
        reference_patterns=reference_patterns,
        output_type=output_type,
        recipient=recipient,
        desired_action=desired_action,
        avoid=avoid,
        success_criteria=success_criteria,
        rules=rules,
        tone=tone,
    )


def build_guided_prompt(blueprint: GuidedPromptBlueprint) -> str:
    lines = [
        "Task:",
        _build_task_line(blueprint),
    ]

    if blueprint.context_files:
        lines.extend(["", "Context Files:", "First, read these completely before responding:"])
        lines.extend(f"- {item}" for item in blueprint.context_files)

    if blueprint.reference_text:
        lines.extend(["", "Reference:", blueprint.reference_text.strip()])

    if blueprint.reference_patterns:
        lines.extend(["", "Reference Patterns To Reuse:"])
        lines.extend(f"- Always {item}" for item in blueprint.reference_patterns)

    lines.extend(["", "Success Brief:"])
    lines.extend(
        [
            f"- Type of output: {blueprint.output_type or 'Choose the most useful format for the task.'}",
            f"- Recipient or audience: {blueprint.recipient or 'Infer the likely audience and state your assumption.'}",
            f"- Desired effect: {blueprint.desired_action or 'Help the reader understand what matters and what to do next.'}",
            f"- Do not sound like: {blueprint.avoid or 'Avoid generic, vague, robotic, or jargon-heavy phrasing.'}",
            f"- Success means: {blueprint.success_criteria or 'The result is clear, useful, and directly usable.'}",
        ]
    )

    lines.extend(["", "Rules:"])
    rule_lines = [
        f"- Keep the response {blueprint.tone}.",
        "- Preserve the original intent and do not add unrelated ideas.",
        "- If any requirement conflicts with the task, call it out instead of guessing.",
    ]
    rule_lines.extend(f"- {item}" for item in blueprint.rules)
    lines.extend(rule_lines)

    lines.extend(
        [
            "",
            "Conversation:",
            "- If anything important is missing, ask clarifying questions before executing.",
            "- If a context file or reference is unclear, say what additional detail would help.",
            "",
            "Plan:",
            "- Before writing, list the 3 rules that matter most for this task.",
            "- Then give a plan in 5 steps maximum.",
            "",
            "Alignment:",
            "- Begin the full answer only after you have aligned on the task, rules, and output format.",
        ]
    )

    return "\n".join(lines).strip()


def _build_task_line(blueprint: GuidedPromptBlueprint) -> str:
    task = blueprint.task.strip()
    success = blueprint.goal.strip() or blueprint.success_criteria.strip()
    if success:
        return f"I want to {task} so that {success}."
    return task


def _ensure_value(current_value: str, question: str) -> str:
    value = current_value.strip()
    while not value:
        value = input(f"{question}\n> ").strip()
    return value


def _ask_optional(current_value: str, question: str) -> str:
    if current_value.strip():
        return current_value.strip()
    return input(f"{question}\n> ").strip()


def _collect_repeating(existing: list[str], intro: str, item_label: str) -> list[str]:
    if existing:
        return [item.strip() for item in existing if item.strip()]

    print(intro)
    results: list[str] = []
    while True:
        value = input(f"{item_label}: ").strip()
        if not value:
            break
        results.append(value)
    return results


def _collect_repeating_optional(existing: list[str], intro: str, item_label: str) -> list[str]:
    if existing:
        return [item.strip() for item in existing if item.strip()]

    print(intro)
    results: list[str] = []
    while True:
        value = input(f"{item_label}: ").strip()
        if not value:
            break
        results.append(value)
    return results


def _should_collect_deep_context(args) -> bool:
    if (
        getattr(args, "context_file", None)
        or getattr(args, "reference", "")
        or getattr(args, "reference_pattern", None)
    ):
        return True
    answer = input(
        "\nDo you want to add reference files or examples, or should I keep this fast? [y/N]\n> "
    ).strip().lower()
    return answer in {"y", "yes"}


def suggest_prompt_upgrades(task: str) -> list[str]:
    lowered = task.lower()
    suggestions = [
        "Say what a strong answer should help the reader do next.",
        "Name the audience so the tone and detail level fit.",
        "Add a format or length target so the output stays usable.",
    ]
    for label, label_suggestions in TASK_TYPE_HINTS.items():
        if label in lowered:
            suggestions.extend(label_suggestions)
            break
    if len(lowered.split()) <= 5:
        suggestions.append("Your starting prompt is short, so even one extra sentence of context will improve the result a lot.")
    return _dedupe(suggestions)[:5]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result
