"""Prompt templates for classification, error analysis, and prompt improvement."""

from __future__ import annotations

import json


DEFAULT_CLASSIFICATION_PROMPT = """You classify short retail banking complaints.

Choose exactly one class label from the allowed list. The labels are short and
may overlap, so rely on the customer's complaint wording.

Confidence rubric:
- 9-10: clear wording points to one label.
- 5-8: the best label is likely, but the complaint has limited detail or overlapping cues.
- 1-4: the complaint is ambiguous, missing details, or could fit multiple labels.

Return JSON only with this shape:
{
  "class_label": "one allowed class label",
  "confidence": 1,
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

Write a proposed prompt that keeps the same JSON output contract and allowed
label set. Make the prompt more discriminative using the error analysis and
sampled error cases provided.

If draft_prompt and review_feedback are provided, rewrite that draft prompt
using the same optimisation context plus the review feedback.

Return JSON only:
{
  "proposed_prompt": "...",
  "change_summary": ["...", "..."]
}
"""


PROMPT_REVIEW_PROMPT = """
You review a proposed text-classification prompt.

Check whether the proposed prompt has highly likely overfitting risks, such as very sample-specific wording, brittle exact phrases, or rules that are too narrowly tied to the provided error cases.
Check whether the prompt includes personal information or asks the classifier to rely on personal information.
Check duplicate or redundant rules.
Check conflicting rules.

For each findings list, include only actual problems. If there are no actual problems for that category, return an empty list. Do not add reassuring notes or cautions as findings.

Only request a rewrite when the issue is material. If the prompt is acceptable, set needs_rewrite to false and leave rewrite_feedback empty.

Return JSON only:
{
  "needs_rewrite": false,
  "overfitting_risks": ["..."],
  "pii_risks": ["..."],
  "duplicate_rules": ["..."],
  "conflicting_rules": ["..."],
  "rewrite_feedback": "..."
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
    *,
    draft_prompt: str | None = None,
    review_feedback: str | None = None,
) -> str:
    payload: dict[str, object] = {
        "current_prompt": current_prompt,
        "allowed_class_labels": class_labels,
        "error_analysis": error_analysis,
        "error_cases": error_cases,
    }
    if draft_prompt is not None:
        payload["draft_prompt"] = draft_prompt
    if review_feedback is not None:
        payload["review_feedback"] = review_feedback
    return json.dumps(payload, indent=2)


def prompt_review_user_prompt(
    current_prompt: str,
    proposed_prompt: str,
    class_labels: list[str],
    error_analysis: dict[str, object],
    error_cases: list[dict[str, object]],
) -> str:
    return json.dumps(
        {
            "current_prompt": current_prompt,
            "proposed_prompt": proposed_prompt,
            "allowed_class_labels": class_labels,
            "error_analysis": error_analysis,
            "error_cases": error_cases,
        },
        indent=2,
    )
