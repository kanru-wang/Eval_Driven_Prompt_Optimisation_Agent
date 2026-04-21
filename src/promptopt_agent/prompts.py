"""Prompt templates for classification, error analysis, and prompt improvement."""

from __future__ import annotations

import json


DEFAULT_CLASSIFICATION_PROMPT = """You classify short retail banking complaints.

Choose exactly one class label from the allowed list. The labels are short and
may overlap, so rely on the customer's complaint wording.

Confidence rubric:
- 0.80-1.00: clear wording points to one label.
- 0.50-0.79: the best label is likely, but the complaint has limited detail or overlapping cues.
- 0.00-0.49: the complaint is ambiguous, missing details, or fit multiple labels.

Return JSON only with this shape:
{
  "class_label": "one allowed class label",
  "confidence": 0.0,
  "rationale": "brief reason using only complaint text"
}
"""


ERROR_ANALYSIS_PROMPT = """You analyse classification errors for retail banking complaints.

Use the confusion matrix and sampled error cases to identify where the prompt is
ambiguous. Do not use hidden labels or external knowledge. Return JSON only:
{
  "summary": "short diagnosis",
  "confusing_pairs": [
    {
      "true_label": "...",
      "predicted_label": "...",
      "likely_reason": "...",
      "prompt_gap": "..."
    }
  ],
  "improvement_principles": ["...", "..."]
}
"""


PROMPT_IMPROVEMENT_PROMPT = """You improve a text-classification prompt.

Write a revised prompt that keeps the same JSON output contract and allowed
label set. Make the prompt more discriminative using only the error analysis
and sampled error cases provided.

Return JSON only:
{
  "proposed_prompt": "...",
  "change_summary": ["...", "..."]
}
"""


def classification_user_prompt(
    class_labels: list[str],
    complaint_text: str,
) -> str:
    return json.dumps(
        {
            "allowed_class_labels": class_labels,
            "complaint_text": complaint_text,
        },
        indent=2,
    )


def analysis_user_prompt(
    class_labels: list[str],
    confusion_matrix: dict[str, dict[str, int]],
    error_cases: list[dict[str, object]],
) -> str:
    return json.dumps(
        {
            "allowed_class_labels": class_labels,
            "confusion_matrix": confusion_matrix,
            "error_cases": error_cases,
        },
        indent=2,
    )


def improvement_user_prompt(
    current_prompt: str,
    class_labels: list[str],
    error_analysis: dict[str, object],
    error_cases: list[dict[str, object]],
) -> str:
    return json.dumps(
        {
            "current_prompt": current_prompt,
            "allowed_class_labels": class_labels,
            "error_analysis": error_analysis,
            "error_cases": error_cases,
        },
        indent=2,
    )
