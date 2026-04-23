"""Command-line interface for the prompt optimisation agent."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Callable

from agent import IterationResult, PromptOptimisationAgent, ScoreResult
from classifier import Prediction
from data_loader import load_samples
from llm import TokenUsage
from taxonomy import CLASS_LABELS


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _prediction_data(predictions: list[Prediction]) -> list[dict[str, object]]:
    return [
        {
            "sample_number": item.sample_number,
            "complaint_text": item.complaint_text,
            "true_label": item.true_label,
            "predicted_label": item.predicted_label,
            "confidence": item.confidence,
            "rationale": item.rationale,
        }
        for item in predictions
    ]


def _token_usage_data(usage: TokenUsage) -> dict[str, int]:
    return {
        "requests": usage.requests,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }


def _score_data(
    result: ScoreResult,
    *,
    prompt_source: str | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "dataset_name": result.dataset_name,
    }
    if prompt_source is not None:
        data["prompt_source"] = prompt_source
    data.update({
        "prompt_used": result.prompt,
        "accuracy": result.accuracy,
        "top_confusions": result.top_confusions,
        "confusion_matrix": result.confusion_matrix,
        "error_cases": result.error_cases,
        "token_usage": _token_usage_data(result.token_usage),
        "predictions": _prediction_data(result.predictions),
    })
    return data


def _write_iteration_artifacts(
    output_dir: Path,
    result: IterationResult,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "iteration": result.iteration,
        "prompt_used": result.prompt,
        "error_analysis": result.error_analysis,
        "initial_change_summary": result.initial_change_summary,
        "change_summary": result.change_summary,
        "prompt_review": result.prompt_review,
        "original_proposed_prompt": result.original_proposed_prompt,
        "proposed_prompt": result.proposed_prompt,
        "training": {
            "dataset_name": "training",
            "prompt_used": result.prompt,
            "accuracy": result.accuracy,
            "top_confusions": result.top_confusions,
            "confusion_matrix": result.confusion_matrix,
            "error_cases": result.error_cases,
            "token_usage": _token_usage_data(result.token_usage["classification"]),
            "predictions": _prediction_data(result.predictions),
        },
        "validation": _score_data(result.validation),
        "token_usage": {
            name: _token_usage_data(usage)
            for name, usage in result.token_usage.items()
        },
    }
    artifact_path = output_dir / f"iteration_{result.iteration:02d}.json"
    used_prompt_path = output_dir / f"prompt_{result.iteration:02d}_used.txt"
    original_proposed_prompt_path = (
        output_dir / f"prompt_{result.iteration:02d}_original_proposed.txt"
    )
    proposed_prompt_path = output_dir / f"prompt_{result.iteration:02d}_proposed.txt"
    artifact_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _save_text(used_prompt_path, result.prompt)
    _save_text(original_proposed_prompt_path, result.original_proposed_prompt)
    _save_text(proposed_prompt_path, result.proposed_prompt)
    return {
        "artifact": artifact_path,
        "used_prompt": used_prompt_path,
        "original_proposed_prompt": original_proposed_prompt_path,
        "proposed_prompt": proposed_prompt_path,
    }


def _write_score_artifact(
    output_dir: Path,
    result: ScoreResult,
    *,
    prompt_source: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / f"{result.dataset_name}_score.json"
    artifact_path.write_text(
        json.dumps(_score_data(result, prompt_source=prompt_source), indent=2),
        encoding="utf-8",
    )
    return artifact_path


def _save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _review_gate(prompt_path: str | Path, ask: Callable[[str], str] = input) -> bool:
    answer = ask(
        "\nEdit the proposed prompt file if needed, then accept it "
        f"for the next iteration? [{prompt_path}] [y/N] "
    )
    return answer.strip().lower() in {"y", "yes"}


def _load_prompt_file(prompt_path: Path, *, description: str = "Prompt") -> str:
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError(f"{description} file is empty: {prompt_path}")
    return prompt


def _load_reviewed_prompt(prompt_path: Path) -> str:
    return _load_prompt_file(prompt_path, description="Reviewed prompt")


def _starting_iteration(initial_prompt_path: str | None) -> int:
    if initial_prompt_path is None:
        return 1
    match = re.search(
        r"prompt_(\d+?)_(?:original_)?(?:proposed|used)\.txt$",
        Path(initial_prompt_path).name,
    )
    if match is None:
        return 1
    return int(match.group(1)) + 1


def _rewrite_happened(result: IterationResult) -> bool:
    return result.token_usage["prompt_rewrite"].requests > 0


def _render_progress(current: int, total: int, usage: TokenUsage) -> None:
    width = 28
    filled = int(width * current / total) if total else width
    bar = "#" * filled + "-" * (width - filled)
    print(
        f"\rClassifying [{bar}] {current}/{total} "
        f"| requests={usage.requests} tokens={usage.total_tokens}",
        end="",
        flush=True,
    )
    if current == total:
        print()


def _print_usage(title: str, usage: TokenUsage) -> None:
    print(
        f"{title}: requests={usage.requests}, "
        f"prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, "
        f"total={usage.total_tokens}"
    )


def _print_section(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print("-" * 72)


def _progress_callback(agent: PromptOptimisationAgent):
    def callback(current: int, total: int, prediction: Prediction) -> None:
        del prediction
        _render_progress(current, total, agent.token_usage)

    return callback


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run eval-driven prompt optimisation for complaint classification."
    )
    parser.add_argument(
        "--training-samples",
        "--samples",
        dest="training_samples",
        default=str(_repo_root() / "data" / "banking_complaint_training_samples.py"),
        help="Path to training Python module containing COMPLAINT_SAMPLES.",
    )
    parser.add_argument(
        "--validation-samples",
        default=str(_repo_root() / "data" / "banking_complaint_validation_samples.py"),
        help="Path to validation Python module containing COMPLAINT_SAMPLES.",
    )
    parser.add_argument(
        "--test-samples",
        default=str(_repo_root() / "data" / "banking_complaint_test_samples.py"),
        help="Path to test Python module containing COMPLAINT_SAMPLES.",
    )
    parser.add_argument(
        "--score-test",
        action="store_true",
        help=(
            "Score the test set once using the prompt passed by --initial-prompt and "
            "exit without running training iterations."
        ),
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
        help="OpenAI model name.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key. Defaults to OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Maximum accepted prompt iterations to run.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_repo_root() / "runs"),
        help="Directory for JSON artifacts and proposed prompts.",
    )
    parser.add_argument(
        "--initial-prompt",
        default=None,
        help="Optional path to a saved prompt file to use for the first iteration.",
    )
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

    initial_prompt = (
        _load_prompt_file(Path(args.initial_prompt), description="Initial prompt")
        if args.initial_prompt
        else None
    )
    agent = PromptOptimisationAgent(
        api_key=args.api_key,
        model=args.model,
        class_labels=CLASS_LABELS,
        **({"initial_prompt": initial_prompt} if initial_prompt is not None else {}),
    )
    if args.initial_prompt:
        print(f"Loaded initial prompt from: {args.initial_prompt}")

    output_dir = Path(args.output_dir)
    if args.score_test:
        if args.initial_prompt is None:
            raise SystemExit(
                "Test scoring requires --initial-prompt pointing to the prompt "
                "file you want to evaluate, for example runs/prompt_01_proposed.txt."
            )
        test_samples = load_samples(args.test_samples)
        print(f"\nScoring test set with {len(test_samples)} samples.")
        score = agent.score_samples(
            test_samples,
            dataset_name="test",
            progress_callback=_progress_callback(agent),
        )
        prompt_source = args.initial_prompt
        artifact_path = _write_score_artifact(
            output_dir,
            score,
            prompt_source=prompt_source,
        )
        print(f"\nTest accuracy: {score.accuracy:.3f}")
        _print_usage("Test scoring", score.token_usage)
        print(f"Prompt source: {prompt_source}")
        print(f"Test score artifact written to: {artifact_path}")
        return

    training_samples = load_samples(args.training_samples)
    validation_samples = load_samples(args.validation_samples)
    start_iteration = _starting_iteration(args.initial_prompt)
    if start_iteration > args.iterations:
        raise SystemExit(
            f"Initial prompt implies starting at iteration {start_iteration}, "
            f"but --iterations is {args.iterations}. Increase --iterations to at "
            f"least {start_iteration} or use an earlier prompt file."
        )

    for iteration in range(start_iteration, args.iterations + 1):
        print(
            f"\nStarting iteration {iteration} with "
            f"{len(training_samples)} training samples."
        )
        result = agent.run_iteration(
            training_samples,
            iteration=iteration,
            validation_samples=validation_samples,
            progress_callback=_progress_callback(agent),
        )
        artifact_paths = _write_iteration_artifacts(output_dir, result)

        _print_section(f"Iteration {iteration}: Training classification")
        print(f"Training accuracy: {result.accuracy:.3f}")
        print("Training top confusions:")
        for item in result.top_confusions:
            print(
                f"- {item['true_label']} -> {item['predicted_label']}: {item['count']}"
            )

        _print_section("Prompt improvement")
        print("Change summary:")
        for item in result.change_summary:
            print(f"- {item}")
        print("\nOriginal proposed prompt:\n")
        print(result.original_proposed_prompt)

        _print_section("Prompt review")
        print(f"- Needs rewrite: {result.prompt_review['needs_rewrite']}")
        for item in result.prompt_review["overfitting_risks"]:
            print(f"- Overfitting risk: {item}")
        for item in result.prompt_review["pii_risks"]:
            print(f"- PII risk: {item}")
        for item in result.prompt_review["duplicate_rules"]:
            print(f"- Duplicate rule: {item}")
        for item in result.prompt_review["conflicting_rules"]:
            print(f"- Conflicting rule: {item}")
        if result.prompt_review["rewrite_feedback"]:
            print(f"- Rewrite feedback: {result.prompt_review['rewrite_feedback']}")

        if _rewrite_happened(result):
            _print_section("Prompt rewrite")
            print("\nFinal proposed prompt after prompt review rewrite:\n")
            print(result.proposed_prompt)

        _print_section("Validation")
        print(f"Validation accuracy: {result.validation.accuracy:.3f}")
        print("Validation top confusions:")
        for item in result.validation.top_confusions:
            print(
                f"- {item['true_label']} -> {item['predicted_label']}: {item['count']}"
            )

        _print_section("Token usage")
        _print_usage("- Classification", result.token_usage["classification"])
        _print_usage("- Error analysis", result.token_usage["error_analysis"])
        _print_usage("- Prompt improvement", result.token_usage["prompt_improvement"])
        _print_usage("- Prompt review", result.token_usage["prompt_review"])
        _print_usage("- Prompt rewrite", result.token_usage["prompt_rewrite"])
        _print_usage("- Validation", result.token_usage["validation"])
        _print_usage("- Iteration total", result.token_usage["iteration_total"])
        _print_usage("- Run total", result.token_usage["run_total"])

        _print_section("Artifacts")
        print(f"Artifacts written to: {output_dir}")
        print(
            "Original proposed prompt: "
            f"{artifact_paths['original_proposed_prompt']}"
        )
        print(f"Review/edit proposed prompt: {artifact_paths['proposed_prompt']}")

        if iteration == args.iterations:
            break
        if not _review_gate(artifact_paths["proposed_prompt"]):
            print("Stopped before applying the proposed prompt.")
            break
        reviewed_prompt = _load_reviewed_prompt(artifact_paths["proposed_prompt"])
        agent.accept_prompt(reviewed_prompt)
        print(f"Accepted prompt from: {artifact_paths['proposed_prompt']}")


if __name__ == "__main__":
    main()
