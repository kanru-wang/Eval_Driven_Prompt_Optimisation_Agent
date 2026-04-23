"""Pydantic schemas for LLM JSON contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ClassificationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    class_label: str = Field(description="Exactly one label from the allowed list.")
    confidence: int = Field(ge=1, le=10)
    rationale: str


class ConfusingPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    true_label: str
    predicted_label: str
    likely_reason: str
    prompt_gap: str


class ErrorAnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    confusing_pairs: list[ConfusingPair]
    improvement_principles: list[str]


class PromptImprovementOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposed_prompt: str
    change_summary: list[str]

    @field_validator("proposed_prompt")
    @classmethod
    def proposed_prompt_must_not_be_empty(cls, value: str) -> str:
        prompt = _normalize_prompt_text(value)
        if not prompt.strip():
            raise ValueError("proposed_prompt must not be empty")
        return prompt


class PromptReviewOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    needs_rewrite: bool
    overfitting_risks: list[str]
    pii_risks: list[str]
    duplicate_rules: list[str]
    conflicting_rules: list[str]
    rewrite_feedback: str

    @field_validator("rewrite_feedback")
    @classmethod
    def rewrite_feedback_must_match_decision(cls, value: str, info) -> str:
        feedback = value.strip()
        if info.data.get("needs_rewrite") and not feedback:
            raise ValueError("rewrite_feedback is required when needs_rewrite is true")
        return feedback


def classification_response_schema(class_labels: list[str]) -> dict[str, Any]:
    schema = ClassificationOutput.model_json_schema()
    schema["properties"]["class_label"]["enum"] = class_labels
    schema["properties"]["confidence"]["enum"] = list(range(1, 11))
    return _openai_strict_schema(schema)


def error_analysis_response_schema() -> dict[str, Any]:
    return _openai_strict_schema(ErrorAnalysisOutput.model_json_schema())


def prompt_improvement_response_schema() -> dict[str, Any]:
    return _openai_strict_schema(PromptImprovementOutput.model_json_schema())


def prompt_review_response_schema() -> dict[str, Any]:
    return _openai_strict_schema(PromptReviewOutput.model_json_schema())


def validate_classification_output(
    result: dict[str, Any],
    class_labels: list[str],
) -> ClassificationOutput:
    output = ClassificationOutput.model_validate(result)
    if output.class_label not in class_labels:
        raise ValueError(
            f"Model returned class_label {output.class_label!r}, "
            "which is not in the allowed class labels."
        )
    return output


def validate_error_analysis_output(result: dict[str, Any]) -> dict[str, Any]:
    return _model_dump(ErrorAnalysisOutput.model_validate(result))


def validate_prompt_improvement_output(result: dict[str, Any]) -> dict[str, Any]:
    return _model_dump(PromptImprovementOutput.model_validate(result))


def validate_prompt_review_output(result: dict[str, Any]) -> dict[str, Any]:
    return _model_dump(PromptReviewOutput.model_validate(result))


def validation_error_message(exc: ValidationError | ValueError) -> str:
    return f"Model output did not match the expected JSON contract: {exc}"


def _model_dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump()


def _normalize_prompt_text(value: str) -> str:
    return (
        value.replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\t", "  ")
        .replace('\\"', '"')
        .strip()
    )


def _openai_strict_schema(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _openai_strict_schema(item)
            for key, item in value.items()
            if key not in {"default", "description", "maximum", "minimum", "title"}
        }
    if isinstance(value, list):
        return [_openai_strict_schema(item) for item in value]
    return value
