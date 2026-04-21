"""LLM-driven error analysis and prompt improvement."""

from __future__ import annotations

from promptopt_agent.llm import OpenAIJSONClient
from promptopt_agent.prompts import (
    ERROR_ANALYSIS_PROMPT,
    PROMPT_IMPROVEMENT_PROMPT,
    analysis_user_prompt,
    improvement_user_prompt,
)
from promptopt_agent.schemas import (
    error_analysis_response_schema,
    prompt_improvement_response_schema,
    validate_error_analysis_output,
    validate_prompt_improvement_output,
    validation_error_message,
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
        result = self._llm.complete_json(
            system_prompt=ERROR_ANALYSIS_PROMPT,
            user_prompt=analysis_user_prompt(
                class_labels=self._class_labels,
                confusion_matrix=confusion_matrix,
                error_cases=error_cases,
            ),
            temperature=0.2,
            response_schema=error_analysis_response_schema(),
            schema_name="error_analysis",
        )
        try:
            return validate_error_analysis_output(result)
        except ValueError as exc:
            raise ValueError(validation_error_message(exc)) from exc

    def improve_prompt(
        self,
        current_prompt: str,
        error_analysis: dict[str, object],
        error_cases: list[dict[str, object]],
    ) -> dict[str, object]:
        result = self._llm.complete_json(
            system_prompt=PROMPT_IMPROVEMENT_PROMPT,
            user_prompt=improvement_user_prompt(
                current_prompt=current_prompt,
                class_labels=self._class_labels,
                error_analysis=error_analysis,
                error_cases=error_cases,
            ),
            temperature=0.3,
            response_schema=prompt_improvement_response_schema(),
            schema_name="prompt_improvement",
        )
        try:
            return validate_prompt_improvement_output(result)
        except ValueError as exc:
            raise ValueError(validation_error_message(exc)) from exc
