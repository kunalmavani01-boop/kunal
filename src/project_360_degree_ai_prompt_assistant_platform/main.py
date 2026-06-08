#!/usr/bin/env python
"""CLI entry point for the prompt assistant MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from project_360_degree_ai_prompt_assistant_platform.assistant import PromptAssistant
from project_360_degree_ai_prompt_assistant_platform.guided import collect_guided_blueprint
from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings
from project_360_degree_ai_prompt_assistant_platform.web_ui import run_browser_app


def run() -> None:
    """Run the original CrewAI planning flow."""
    from project_360_degree_ai_prompt_assistant_platform.crew import (
        Project360DegreeAiPromptAssistantPlatformCrew,
    )

    inputs = {"project_type": "local-first prompt assistant"}
    Project360DegreeAiPromptAssistantPlatformCrew().crew().kickoff(inputs=inputs)


def train() -> None:
    """Train the CrewAI planning flow."""
    from project_360_degree_ai_prompt_assistant_platform.crew import (
        Project360DegreeAiPromptAssistantPlatformCrew,
    )

    inputs = {"project_type": "local-first prompt assistant"}
    args = [item for item in sys.argv[1:] if item != "train"]
    try:
        Project360DegreeAiPromptAssistantPlatformCrew().crew().train(
            n_iterations=int(args[0]),
            filename=args[1],
            inputs=inputs,
        )
    except Exception as exc:  # pragma: no cover - passthrough helper
        raise Exception(f"An error occurred while training the crew: {exc}") from exc


def replay() -> None:
    """Replay a CrewAI task."""
    from project_360_degree_ai_prompt_assistant_platform.crew import (
        Project360DegreeAiPromptAssistantPlatformCrew,
    )

    args = [item for item in sys.argv[1:] if item != "replay"]
    try:
        Project360DegreeAiPromptAssistantPlatformCrew().crew().replay(task_id=args[0])
    except Exception as exc:  # pragma: no cover - passthrough helper
        raise Exception(f"An error occurred while replaying the crew: {exc}") from exc


def test() -> None:
    """Test the CrewAI planning flow."""
    from project_360_degree_ai_prompt_assistant_platform.crew import (
        Project360DegreeAiPromptAssistantPlatformCrew,
    )

    inputs = {"project_type": "local-first prompt assistant"}
    args = [item for item in sys.argv[1:] if item != "test"]
    try:
        Project360DegreeAiPromptAssistantPlatformCrew().crew().test(
            n_iterations=int(args[0]),
            openai_model_name=args[1],
            inputs=inputs,
        )
    except Exception as exc:  # pragma: no cover - passthrough helper
        raise Exception(f"An error occurred while testing the crew: {exc}") from exc


def run_with_trigger() -> None:
    """Compatibility alias for older script wiring."""
    run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-assistant",
        description="Review, strengthen, and remember prompts locally.",
    )
    subparsers = parser.add_subparsers(dest="command")

    improve_parser = subparsers.add_parser(
        "improve",
        help="Analyze a prompt and generate a stronger version.",
    )
    improve_parser.add_argument("prompt", nargs="*", help="Prompt text to improve.")
    improve_parser.add_argument(
        "--file",
        type=Path,
        help="Read the prompt from a text file.",
    )
    improve_parser.add_argument(
        "--context",
        default="",
        help="Extra background that should shape the improved prompt.",
    )
    improve_parser.add_argument(
        "--output-format",
        default="",
        help="Requested output shape such as bullet list, JSON, or email.",
    )
    improve_parser.add_argument(
        "--constraint",
        action="append",
        default=[],
        help="Add a hard requirement. Use the flag multiple times for multiple constraints.",
    )
    improve_parser.add_argument(
        "--tone",
        default="clear and practical",
        help="Preferred writing tone for the improved prompt.",
    )
    improve_parser.add_argument(
        "--provider",
        choices=["local", "openai", "gemini"],
        default="local",
        help="Optional live provider to test against after the local rewrite.",
    )
    improve_parser.add_argument(
        "--model",
        default="",
        help="Override the provider model name.",
    )
    improve_parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="How many relevant memories to reuse.",
    )
    improve_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full result as JSON.",
    )
    improve_parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not store this prompt in local memory.",
    )

    guide_parser = subparsers.add_parser(
        "guide",
        help="Ask for the right inputs, structure them, and rebuild the prompt.",
    )
    guide_parser.add_argument("--task", default="", help="What the model should do.")
    guide_parser.add_argument("--goal", default="", help="What success should achieve.")
    guide_parser.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="A context file and what it contains. Example: brief.md - brand and audience.",
    )
    guide_parser.add_argument("--reference", default="", help="Reference text or example to emulate.")
    guide_parser.add_argument(
        "--reference-pattern",
        action="append",
        default=[],
        help="A pattern to reuse from the reference.",
    )
    guide_parser.add_argument("--output-type", default="", help="Desired output type.")
    guide_parser.add_argument("--recipient", default="", help="Audience or recipient.")
    guide_parser.add_argument("--desired-action", default="", help="What the reader should think, feel, or do.")
    guide_parser.add_argument("--avoid", default="", help="What style or tone to avoid.")
    guide_parser.add_argument("--success", default="", help="How success should be judged.")
    guide_parser.add_argument(
        "--rule",
        action="append",
        default=[],
        help="Hard rule or constraint. Use the flag multiple times.",
    )
    guide_parser.add_argument("--tone", default="clear and practical", help="Preferred tone.")
    guide_parser.add_argument(
        "--provider",
        choices=["local", "openai", "gemini"],
        default="local",
        help="Optional live provider to test against after structuring.",
    )
    guide_parser.add_argument("--model", default="", help="Override the provider model name.")
    guide_parser.add_argument("--top-k", type=int, default=None, help="How many memories to reuse.")
    guide_parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    guide_parser.add_argument("--no-save", action="store_true", help="Do not store this prompt in local memory.")

    history_parser = subparsers.add_parser(
        "history",
        help="Show recent prompts stored in local memory.",
    )
    history_parser.add_argument("--limit", type=int, default=10)

    feedback_parser = subparsers.add_parser(
        "feedback",
        help="Attach feedback to a saved prompt entry.",
    )
    feedback_parser.add_argument("entry_id", type=int, help="Saved entry number.")
    feedback_parser.add_argument("feedback", help="What worked or did not work.")
    feedback_parser.add_argument(
        "--rating",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Optional 1-5 quality score.",
    )

    subparsers.add_parser("gui", help="Open the browser MVP.")
    subparsers.add_parser("web", help="Open the browser MVP.")
    subparsers.add_parser("config", help="Show local storage and provider setup.")
    subparsers.add_parser("run-crew", help="Run the original CrewAI planning flow.")

    train_parser = subparsers.add_parser("train-crew", help="Train the CrewAI flow.")
    train_parser.add_argument("iterations", type=int)
    train_parser.add_argument("filename")

    replay_parser = subparsers.add_parser("replay-crew", help="Replay a CrewAI task.")
    replay_parser.add_argument("task_id")

    test_parser = subparsers.add_parser("test-crew", help="Test the CrewAI flow.")
    test_parser.add_argument("iterations", type=int)
    test_parser.add_argument("model")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "run-crew":
        run()
        return 0

    if args.command == "train-crew":
        sys.argv = [sys.argv[0], "train", str(args.iterations), args.filename]
        train()
        return 0

    if args.command == "replay-crew":
        sys.argv = [sys.argv[0], "replay", args.task_id]
        replay()
        return 0

    if args.command == "test-crew":
        sys.argv = [sys.argv[0], "test", str(args.iterations), args.model]
        test()
        return 0

    assistant = PromptAssistant(AppSettings.from_env())

    if args.command == "gui":
        run_browser_app(assistant)
        return 0

    if args.command == "web":
        run_browser_app(assistant)
        return 0

    if args.command == "config":
        print(render_config(assistant.settings))
        return 0

    if args.command == "history":
        entries = assistant.history(limit=args.limit)
        print(render_history(entries))
        return 0

    if args.command == "feedback":
        assistant.record_feedback(
            entry_id=args.entry_id,
            feedback=args.feedback,
            rating=args.rating,
        )
        print(f"Saved feedback for entry #{args.entry_id}.")
        return 0

    if args.command == "improve":
        prompt_text = load_prompt_text(args)
        result = assistant.improve_prompt(
            prompt=prompt_text,
            extra_context=args.context,
            output_format=args.output_format,
            constraints=args.constraint,
            tone=args.tone,
            provider=args.provider,
            model=args.model or None,
            top_k=args.top_k,
            save=not args.no_save,
        )
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(render_result(result))
        return 0

    if args.command == "guide":
        blueprint = collect_guided_blueprint(args)
        result = assistant.guide_prompt(
            blueprint=blueprint,
            provider=args.provider,
            model=args.model or None,
            top_k=args.top_k,
            save=not args.no_save,
        )
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(render_result(result))
        return 0

    parser.print_help()
    return 1


def load_prompt_text(args: argparse.Namespace) -> str:
    if args.file:
        return args.file.read_text(encoding="utf-8").strip()

    if args.prompt:
        return " ".join(args.prompt).strip()

    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    raise SystemExit("Provide a prompt as text, via --file, or through standard input.")


def render_result(result) -> str:
    lines = [
        "Prompt Review",
        "=============",
        "",
        f"Original score: {result.analysis.score}/100",
        f"Re-evaluated score: {result.final_analysis.score}/100",
        f"Saved entry: #{result.entry_id}" if result.entry_id is not None else "Saved entry: not stored",
        "",
        "Strengths in the starting prompt:",
    ]
    if result.analysis.strengths:
        lines.extend(f"- {item}" for item in result.analysis.strengths)
    else:
        lines.append("- No strong signal yet; the prompt needs more structure.")

    lines.extend(["", "Gaps to fix in the starting prompt:"])
    if result.analysis.gaps:
        lines.extend(f"- {item}" for item in result.analysis.gaps)
    else:
        lines.append("- None. The prompt already covers the key ingredients.")

    lines.extend(["", "Suggested improvements:"])
    lines.extend(f"- {item}" for item in result.analysis.suggestions)

    if result.memories:
        lines.extend(["", "Relevant local memory:"])
        for memory in result.memories:
            lines.append(
                f"- #{memory['id']} | {memory['created_at']} | {memory['prompt_preview']}"
            )

    lines.extend(["", "Improved prompt", "---------------", result.improved_prompt])

    lines.extend(["", "Why the rebuilt prompt is stronger", "-------------------------------"])
    if result.final_analysis.strengths:
        lines.extend(f"- {item}" for item in result.final_analysis.strengths[:6])
    else:
        lines.append("- The rebuilt prompt is cleaner, but it may still need more specifics.")

    if result.provider_output:
        lines.extend(
            [
                "",
                f"{result.provider.title()} model rewrite",
                "------------------------",
                result.provider_output,
            ]
        )

    return "\n".join(lines)


def render_history(entries: list[dict]) -> str:
    if not entries:
        return "No prompt history yet."

    lines = ["Recent Prompt History", "=====================", ""]
    for entry in entries:
        rating = entry["rating"] if entry["rating"] is not None else "-"
        lines.extend(
            [
                f"#{entry['id']} | {entry['created_at']} | rating: {rating}",
                f"Prompt: {entry['prompt_preview']}",
                f"Improved: {entry['improved_preview']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_config(settings: AppSettings) -> str:
    return "\n".join(
        [
            "Prompt Assistant Config",
            "=======================",
            "",
            f"App home: {settings.app_home}",
            f"Memory DB: {settings.db_path}",
            f"Default provider: {settings.default_provider}",
            f"Default OpenAI model: {settings.openai_model}",
            f"Default Gemini model: {settings.gemini_model}",
            "",
            "Optional environment variables:",
            "- OPENAI_API_KEY",
            "- GEMINI_API_KEY",
            "- PROMPT_ASSISTANT_HOME",
            "- PROMPT_ASSISTANT_DB",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
