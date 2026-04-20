"""LLM-driven error analysis and prompt improvement."""

from __future__ import annotations

from promptopt_agent.llm import OpenAIJSONClient
from promptopt_agent.prompts import (
    ERROR_ANALYSIS_PROMPT,
    PROMPT_IMPROVEMENT_PROMPT,
    analysis_user_prompt,
    improvement_user_prompt,
)


class LLMPromptOptimizer:
    def __init__(self, llm: OpenAIJSONClient, class_labels: list[str]) -> None:
        self._llm = llm
        self._class_labels = class_labels

    def analyse_errors(
        self,
        confusion_matrix: dict[str, dict[str, int]],
        error_cases: list[dict[str, object]],
    ) -> dict[str, object]:
        return self._llm.complete_json(
            system_prompt=ERROR_ANALYSIS_PROMPT,
            user_prompt=analysis_user_prompt(
                class_labels=self._class_labels,
                confusion_matrix=confusion_matrix,
                error_cases=error_cases,
            ),
            temperature=0.2,
        )

    def improve_prompt(
        self,
        current_prompt: str,
        error_analysis: dict[str, object],
        error_cases: list[dict[str, object]],
    ) -> dict[str, object]:
        return self._llm.complete_json(
            system_prompt=PROMPT_IMPROVEMENT_PROMPT,
            user_prompt=improvement_user_prompt(
                current_prompt=current_prompt,
                class_labels=self._class_labels,
                error_analysis=error_analysis,
                error_cases=error_cases,
            ),
            temperature=0.3,
        )
