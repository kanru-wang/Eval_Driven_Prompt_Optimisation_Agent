"""Command-line interface for the prompt optimisation agent."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Callable

from promptopt_agent.agent import IterationResult, PromptOptimisationAgent
from promptopt_agent.classifier import Prediction
from promptopt_agent.data_loader import load_samples
from promptopt_agent.llm import TokenUsage
from promptopt_agent.taxonomy import CLASS_LABELS


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_iteration_artifacts(
    output_dir: Path,
    result: IterationResult,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "iteration": result.iteration,
        "prompt_used": result.prompt,
        "accuracy": result.accuracy,
        "top_confusions": result.top_confusions,
        "confusion_matrix": result.confusion_matrix,
        "error_cases": result.error_cases,
        "error_analysis": result.error_analysis,
        "change_summary": result.change_summary,
        "proposed_prompt": result.proposed_prompt,
        "token_usage": {
            name: {
                "requests": usage.requests,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }
            for name, usage in result.token_usage.items()
        },
        "predictions": [
            {
                "sample_number": item.sample_number,
                "complaint_text": item.complaint_text,
                "true_label": item.true_label,
                "predicted_label": item.predicted_label,
                "confidence": item.confidence,
                "rationale": item.rationale,
            }
            for item in result.predictions
        ],
    }
    artifact_path = output_dir / f"iteration_{result.iteration:02d}.json"
    used_prompt_path = output_dir / f"prompt_{result.iteration:02d}_used.txt"
    proposed_prompt_path = output_dir / f"prompt_{result.iteration:02d}_proposed.txt"
    artifact_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _save_text(used_prompt_path, result.prompt)
    _save_text(proposed_prompt_path, result.proposed_prompt)
    return {
        "artifact": artifact_path,
        "used_prompt": used_prompt_path,
        "proposed_prompt": proposed_prompt_path,
    }


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
        "--samples",
        default=str(_repo_root() / "banking_complaint_samples.py"),
        help="Path to Python module containing COMPLAINT_SAMPLES.",
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

    samples = load_samples(args.samples)
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
    for iteration in range(1, args.iterations + 1):
        print(f"\nStarting iteration {iteration} with {len(samples)} samples.")
        result = agent.run_iteration(
            samples,
            iteration=iteration,
            progress_callback=_progress_callback(agent),
        )
        artifact_paths = _write_iteration_artifacts(output_dir, result)

        print(f"\nIteration {iteration}")
        print(f"Accuracy: {result.accuracy:.3f}")
        print("Token usage:")
        _print_usage("- Classification", result.token_usage["classification"])
        _print_usage("- Error analysis", result.token_usage["error_analysis"])
        _print_usage("- Prompt improvement", result.token_usage["prompt_improvement"])
        _print_usage("- Iteration total", result.token_usage["iteration_total"])
        _print_usage("- Run total", result.token_usage["run_total"])
        print("Top confusions:")
        for item in result.top_confusions:
            print(
                f"- {item['true_label']} -> {item['predicted_label']}: {item['count']}"
            )
        print("\nChange summary:")
        for item in result.change_summary:
            print(f"- {item}")
        print("\nProposed prompt:\n")
        print(result.proposed_prompt)
        print(f"\nArtifacts written to: {output_dir}")
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
