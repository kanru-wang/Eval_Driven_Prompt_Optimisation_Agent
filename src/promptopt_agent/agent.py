"""Orchestrates classify, evaluate, analyse, improve, and review iterations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from promptopt_agent.classifier import LLMComplaintClassifier, Prediction
from promptopt_agent.data_loader import ComplaintSample
from promptopt_agent.evaluation import accuracy, build_confusion_matrix, error_cases, top_confusions
from promptopt_agent.llm import OpenAIJSONClient, TokenUsage
from promptopt_agent.optimizer import LLMPromptOptimizer
from promptopt_agent.prompts import DEFAULT_CLASSIFICATION_PROMPT


@dataclass(frozen=True)
class ScoreResult:
    dataset_name: str
    prompt: str
    predictions: list[Prediction]
    accuracy: float
    confusion_matrix: dict[str, dict[str, int]]
    top_confusions: list[dict[str, object]]
    error_cases: list[dict[str, object]]
    token_usage: TokenUsage


@dataclass(frozen=True)
class IterationResult:
    iteration: int
    prompt: str
    predictions: list[Prediction]
    accuracy: float
    confusion_matrix: dict[str, dict[str, int]]
    top_confusions: list[dict[str, object]]
    error_cases: list[dict[str, object]]
    error_analysis: dict[str, object]
    proposed_prompt: str
    change_summary: list[str]
    validation: ScoreResult
    token_usage: dict[str, TokenUsage]


class PromptOptimisationAgent:
    def __init__(
        self,
        api_key: str,
        model: str,
        class_labels: list[str],
        *,
        initial_prompt: str = DEFAULT_CLASSIFICATION_PROMPT,
    ) -> None:
        self._llm = OpenAIJSONClient(api_key=api_key, model=model)
        self._class_labels = class_labels
        self._prompt = initial_prompt

    @property
    def current_prompt(self) -> str:
        return self._prompt

    @property
    def token_usage(self) -> TokenUsage:
        return self._llm.usage

    def run_iteration(
        self,
        samples: list[ComplaintSample],
        *,
        iteration: int,
        validation_samples: list[ComplaintSample],
        max_error_cases: int = 30,
        progress_callback: Callable[[int, int, Prediction], None] | None = None,
    ) -> IterationResult:
        iteration_start_usage = self._llm.usage
        classifier = LLMComplaintClassifier(
            llm=self._llm,
            class_labels=self._class_labels,
            classification_prompt=self._prompt,
        )
        predictions = classifier.classify_many(
            samples,
            progress_callback=progress_callback,
        )
        classification_usage = self._llm.usage - iteration_start_usage
        matrix = build_confusion_matrix(predictions, self._class_labels)
        selected_errors = error_cases(predictions, max_cases=max_error_cases)

        optimizer = LLMPromptOptimizer(llm=self._llm, class_labels=self._class_labels)
        analysis_start_usage = self._llm.usage
        analysis = optimizer.analyse_errors(matrix, selected_errors)
        analysis_usage = self._llm.usage - analysis_start_usage
        improvement_start_usage = self._llm.usage
        improvement = optimizer.improve_prompt(
            current_prompt=self._prompt,
            error_analysis=analysis,
            error_cases=selected_errors,
        )
        improvement_usage = self._llm.usage - improvement_start_usage

        proposed_prompt = str(improvement.get("proposed_prompt", self._prompt))
        change_summary = [
            str(item) for item in improvement.get("change_summary", [])
        ]
        validation = self.score_samples(
            validation_samples,
            dataset_name="validation",
            prompt=proposed_prompt,
            max_error_cases=max_error_cases,
            progress_callback=progress_callback,
        )

        return IterationResult(
            iteration=iteration,
            prompt=self._prompt,
            predictions=predictions,
            accuracy=accuracy(predictions),
            confusion_matrix=matrix,
            top_confusions=top_confusions(predictions),
            error_cases=selected_errors,
            error_analysis=analysis,
            proposed_prompt=proposed_prompt,
            change_summary=change_summary,
            validation=validation,
            token_usage={
                "classification": classification_usage,
                "error_analysis": analysis_usage,
                "prompt_improvement": improvement_usage,
                "validation": validation.token_usage,
                "iteration_total": self._llm.usage - iteration_start_usage,
                "run_total": self._llm.usage,
            },
        )

    def accept_prompt(self, proposed_prompt: str) -> None:
        self._prompt = proposed_prompt

    def score_samples(
        self,
        samples: list[ComplaintSample],
        *,
        dataset_name: str,
        prompt: str | None = None,
        max_error_cases: int = 30,
        progress_callback: Callable[[int, int, Prediction], None] | None = None,
    ) -> ScoreResult:
        score_start_usage = self._llm.usage
        prompt_to_score = self._prompt if prompt is None else prompt
        classifier = LLMComplaintClassifier(
            llm=self._llm,
            class_labels=self._class_labels,
            classification_prompt=prompt_to_score,
        )
        predictions = classifier.classify_many(
            samples,
            progress_callback=progress_callback,
        )
        return ScoreResult(
            dataset_name=dataset_name,
            prompt=prompt_to_score,
            predictions=predictions,
            accuracy=accuracy(predictions),
            confusion_matrix=build_confusion_matrix(predictions, self._class_labels),
            top_confusions=top_confusions(predictions),
            error_cases=error_cases(predictions, max_cases=max_error_cases),
            token_usage=self._llm.usage - score_start_usage,
        )
