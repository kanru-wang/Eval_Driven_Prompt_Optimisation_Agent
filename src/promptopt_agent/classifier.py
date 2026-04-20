"""LLM text classifier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from promptopt_agent.data_loader import ComplaintSample
from promptopt_agent.llm import OpenAIJSONClient
from promptopt_agent.prompts import classification_user_prompt


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
        )
        predicted_label = str(result.get("class_label", "")).strip()
        if predicted_label not in self._class_labels:
            predicted_label = "INVALID_LABEL"

        return Prediction(
            sample_number=sample.sample_number,
            complaint_text=sample.complaint_text,
            predicted_label=predicted_label,
            confidence=float(result.get("confidence", 0.0)),
            rationale=str(result.get("rationale", "")),
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
