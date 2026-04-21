"""LLM text classifier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from promptopt_agent.data_loader import ComplaintSample
from promptopt_agent.llm import OpenAIJSONClient
from promptopt_agent.prompts import classification_user_prompt
from promptopt_agent.schemas import (
    classification_response_schema,
    validate_classification_output,
    validation_error_message,
)


@dataclass(frozen=True)
class Prediction:
    sample_number: int
    complaint_text: str
    predicted_label: str
    confidence: float
    rationale: str
    true_label: str | None = None


class LLMComplaintClassifier:
    def __init__(
        self,
        llm: OpenAIJSONClient,
        class_labels: list[str],
        classification_prompt: str,
    ) -> None:
        self._llm = llm
        self._class_labels = class_labels
        self._classification_prompt = classification_prompt

    def classify_one(self, sample: ComplaintSample) -> Prediction:
        result = self._llm.complete_json(
            system_prompt=self._classification_prompt,
            user_prompt=classification_user_prompt(
                class_labels=self._class_labels,
                complaint_text=sample.complaint_text,
            ),
            response_schema=classification_response_schema(self._class_labels),
            schema_name="complaint_classification",
        )
        try:
            output = validate_classification_output(result, self._class_labels)
        except ValueError as exc:
            raise ValueError(validation_error_message(exc)) from exc

        return Prediction(
            sample_number=sample.sample_number,
            complaint_text=sample.complaint_text,
            predicted_label=output.class_label,
            confidence=output.confidence,
            rationale=output.rationale,
            true_label=sample.class_label,
        )

    def classify_many(
        self,
        samples: list[ComplaintSample],
        *,
        progress_callback: Callable[[int, int, Prediction], None] | None = None,
    ) -> list[Prediction]:
        predictions = []
        total = len(samples)
        for index, sample in enumerate(samples, start=1):
            prediction = self.classify_one(sample)
            predictions.append(prediction)
            if progress_callback is not None:
                progress_callback(index, total, prediction)
        return predictions
