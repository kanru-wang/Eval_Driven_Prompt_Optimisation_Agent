"""Evaluation helpers for classification outputs."""

from __future__ import annotations

from collections import Counter

from promptopt_agent.classifier import Prediction


def build_confusion_matrix(
    predictions: list[Prediction],
    class_labels: list[str],
) -> dict[str, dict[str, int]]:
    matrix = {
        actual: {predicted: 0 for predicted in class_labels}
        for actual in class_labels
    }
    for prediction in predictions:
        if prediction.true_label is None:
            continue
        matrix[prediction.true_label][prediction.predicted_label] += 1
    return matrix


def accuracy(predictions: list[Prediction]) -> float:
    labelled = [item for item in predictions if item.true_label is not None]
    if not labelled:
        return 0.0
    correct = sum(1 for item in labelled if item.true_label == item.predicted_label)
    return correct / len(labelled)


def error_cases(
    predictions: list[Prediction],
    *,
    max_cases: int = 30,
) -> list[dict[str, object]]:
    errors = [
        {
            "sample_number": item.sample_number,
            "complaint_text": item.complaint_text,
            "true_label": item.true_label,
            "predicted_label": item.predicted_label,
            "confidence": item.confidence,
            "rationale": item.rationale,
        }
        for item in predictions
        if item.true_label != item.predicted_label
    ]
    errors.sort(key=lambda item: (-int(item["confidence"]), int(item["sample_number"])))
    return errors[:max_cases]


def top_confusions(
    predictions: list[Prediction],
    *,
    max_pairs: int = 10,
) -> list[dict[str, object]]:
    counter: Counter[tuple[str | None, str]] = Counter()
    for item in predictions:
        if item.true_label != item.predicted_label:
            counter[(item.true_label, item.predicted_label)] += 1
    return [
        {"true_label": true_label, "predicted_label": predicted_label, "count": count}
        for (true_label, predicted_label), count in counter.most_common(max_pairs)
    ]
