"""High-level prompt assistant orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from project_360_degree_ai_prompt_assistant_platform.guided import (
    GuidedPromptBlueprint,
    build_guided_prompt,
)
from project_360_degree_ai_prompt_assistant_platform.memory import PromptMemoryStore
from project_360_degree_ai_prompt_assistant_platform.optimizer import (
    PromptAnalysis,
    analyze_prompt,
    build_improved_prompt,
)
from project_360_degree_ai_prompt_assistant_platform.providers import (
    ProviderError,
    generate_with_provider,
)
from project_360_degree_ai_prompt_assistant_platform.prompt_library import PromptLibrary
from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings


@dataclass
class PromptResult:
    entry_id: int | None
    provider: str
    model: str | None
    analysis: PromptAnalysis
    final_analysis: PromptAnalysis
    improved_prompt: str
    provider_output: str
    memories: list[dict]
    recommendations: list[dict]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["analysis"] = self.analysis.to_dict()
        return payload


@dataclass
class PromptInspection:
    analysis: PromptAnalysis
    recommendations: list[dict]

    def to_dict(self) -> dict:
        return {
            "analysis": self.analysis.to_dict(),
            "recommendations": self.recommendations,
        }


class PromptAssistant:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.settings.ensure_app_home()
        self.store = PromptMemoryStore(settings.db_path)
        self.library = PromptLibrary(settings)

    def improve_prompt(
        self,
        *,
        prompt: str,
        extra_context: str = "",
        output_format: str = "",
        constraints: list[str] | None = None,
        tone: str = "clear and practical",
        provider: str | None = None,
        model: str | None = None,
        top_k: int | None = None,
        save: bool = True,
    ) -> PromptResult:
        provider = provider or self.settings.default_provider
        memories = self.store.similar(prompt, limit=top_k or self.settings.memory_limit)
        analysis = analyze_prompt(
            prompt,
            extra_context=extra_context,
            output_format=output_format,
            constraints=constraints,
        )
        recommendations = [item.to_dict() for item in self.library.recommend(prompt)]
        improved_prompt = build_improved_prompt(
            prompt,
            analysis,
            memories=memories,
            extra_context=extra_context,
            output_format=output_format,
            constraints=constraints,
            tone=tone,
        )
        final_analysis = analyze_prompt(
            improved_prompt,
            extra_context=extra_context,
            output_format=output_format,
            constraints=constraints,
        )

        provider_output = ""
        if provider != "local":
            try:
                provider_output = generate_with_provider(
                    provider=provider,
                    prompt=improved_prompt,
                    model=model,
                    settings=self.settings,
                )
            except ProviderError as exc:
                provider_output = f"Provider unavailable: {exc}"

        entry_id = None
        if save:
            stored_output = improved_prompt
            if provider_output and not provider_output.startswith("Provider unavailable:"):
                stored_output = provider_output
            entry_id = self.store.add_entry(
                prompt=prompt,
                improved_prompt=stored_output,
                analysis={
                    **analysis.to_dict(),
                    "final_analysis": final_analysis.to_dict(),
                    "provider": provider,
                    "model": model,
                    "extra_context": extra_context,
                    "output_format": output_format,
                    "constraints": constraints or [],
                },
                tags=analysis.keywords[:5],
            )

        return PromptResult(
            entry_id=entry_id,
            provider=provider,
            model=model,
            analysis=analysis,
            final_analysis=final_analysis,
            improved_prompt=improved_prompt,
            provider_output=provider_output,
            memories=memories,
            recommendations=recommendations,
        )

    def guide_prompt(
        self,
        *,
        blueprint: GuidedPromptBlueprint,
        provider: str | None = None,
        model: str | None = None,
        top_k: int | None = None,
        save: bool = True,
    ) -> PromptResult:
        provider = provider or self.settings.default_provider
        source_prompt = blueprint.task
        source_context = " ".join(
            item
            for item in [
                blueprint.goal,
                blueprint.reference_text,
                blueprint.output_type,
                blueprint.recipient,
                blueprint.desired_action,
                blueprint.avoid,
                blueprint.success_criteria,
            ]
            if item
        )
        memories = self.store.similar(source_prompt, limit=top_k or self.settings.memory_limit)
        analysis = analyze_prompt(
            source_prompt,
            extra_context=source_context,
            output_format=blueprint.output_type,
            constraints=blueprint.rules,
        )
        recommendations = [item.to_dict() for item in self.library.recommend(source_prompt)]
        improved_prompt = build_guided_prompt(blueprint)
        final_analysis = analyze_prompt(
            improved_prompt,
            extra_context=source_context,
            output_format=blueprint.output_type,
            constraints=blueprint.rules,
        )

        provider_output = ""
        if provider != "local":
            try:
                provider_output = generate_with_provider(
                    provider=provider,
                    prompt=improved_prompt,
                    model=model,
                    settings=self.settings,
                )
            except ProviderError as exc:
                provider_output = f"Provider unavailable: {exc}"

        entry_id = None
        if save:
            stored_output = improved_prompt
            if provider_output and not provider_output.startswith("Provider unavailable:"):
                stored_output = provider_output
            entry_id = self.store.add_entry(
                prompt=source_prompt,
                improved_prompt=stored_output,
                analysis={
                    **analysis.to_dict(),
                    "final_analysis": final_analysis.to_dict(),
                    "blueprint": blueprint.to_dict(),
                    "provider": provider,
                    "model": model,
                },
                tags=final_analysis.keywords[:5] or analysis.keywords[:5],
            )

        return PromptResult(
            entry_id=entry_id,
            provider=provider,
            model=model,
            analysis=analysis,
            final_analysis=final_analysis,
            improved_prompt=improved_prompt,
            provider_output=provider_output,
            memories=memories,
            recommendations=recommendations,
        )

    def inspect_prompt(
        self,
        *,
        prompt: str,
        extra_context: str = "",
        output_format: str = "",
        constraints: list[str] | None = None,
    ) -> PromptInspection:
        analysis = analyze_prompt(
            prompt,
            extra_context=extra_context,
            output_format=output_format,
            constraints=constraints,
        )
        recommendations = [item.to_dict() for item in self.library.recommend(prompt)]
        return PromptInspection(analysis=analysis, recommendations=recommendations)

    def history(self, limit: int = 10) -> list[dict]:
        return self.store.recent(limit=limit)

    def history_full(self, limit: int = 20) -> list[dict]:
        return self.store.recent_full(limit=limit)

    def record_feedback(self, *, entry_id: int, feedback: str, rating: int | None = None) -> None:
        self.store.add_feedback(entry_id=entry_id, feedback=feedback, rating=rating)
