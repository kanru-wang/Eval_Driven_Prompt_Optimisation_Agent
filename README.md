# Eval Driven Prompt Optimisation Agent

This project is a small prototype for iterative LLM-based text classification. **Main steps are: (1) LLM classifies retail banking customers' complaints, (2) LLM analyses errors and confusion patterns, (3) LLM proposes a better classification prompt, (4) An LLM-as-a-judge agent checks the proposed prompt for any issue in rules (overfitting, redundant or conflicting) and PII leakage, and decides whether to redo Step 3 or go to Step 5, (5) Wait for human approval/edits, (6) Run the next iteration.**

**The end product is an optimised text classification prompt.**

In this prototype, "training the model" means updating the classification prompt. The classification prompt is the model parameter being reviewed, accepted, and carried into later iterations.

The dummy datasets used are carefully designed so that the LLM is not able to infer which label to choose just from the meaning of each label. It must summarise a map that links (a) the hidden highly-indicative keywords from the complaints and (b) the labels.

## Important Boundary

The classifier sees:

- the complaint text
- the allowed class labels
- the current classification prompt

The classifier does not see:

- `data/banking_complaint_class_keywords.py`
- the sample's ground-truth label during classification

Ground-truth labels from `data/banking_complaint_training_samples.py`,
`data/banking_complaint_validation_samples.py`, and
`data/banking_complaint_test_samples.py`
are only used after prediction to build confusion matrices and error cases.

## Setup

```bash
pip install -e .
```

This installs the `promptopt-agent` console command and makes the modules in
`src/` importable from your environment.

Set your API key:

```bash
set OPENAI_API_KEY=your_key_here
```

On PowerShell:

```powershell
$env:OPENAI_API_KEY = "your_key_here"
```

## Run

By default, the agent uses `gpt-5-nano`. You can override this with
`OPENAI_MODEL` or `--model`.

```bash
promptopt-agent --iterations 3
```

Or run directly from the source tree by putting `src/` on `PYTHONPATH`.

On PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m cli --iterations 3
```

If you already ran `pip install -e .`, this also works:

```bash
python -m cli --iterations 3
```

Each training iteration scores the training set, proposes an updated prompt, reviews it for over-specific wording, PII, duplicate rules, and conflicting rules, optionally rewrites it once, then scores the validation set with the final proposed prompt in `runs/prompt_*_proposed.txt`. Both `training` and `validation` results are recorded.

At the end of each iteration, **You may manually edit `runs/prompt_*_proposed.txt`** before answering the terminal prompt. When you type `y`, the agent reloads the saved `runs/prompt_*_proposed.txt` and uses that reviewed/edited prompt for the next iteration.

To resume later from a saved prompt file, pass `--initial-prompt`:

```bash
promptopt-agent --initial-prompt runs/prompt_01_proposed.txt --iterations 2
```

When `--initial-prompt` points to a saved `prompt_XX_*.txt` file, the CLI
infers that the next run should continue at iteration `XX + 1`. For example,
resuming from `runs/prompt_01_proposed.txt --iterations 2` runs iteration 2 and
writes `runs/iteration_02.json`.

To score the held-out test set separately from the training loop, pass `--score-test`. For final testing, provide the reviewed `*_proposed.txt` prompt you want to score:

```bash
promptopt-agent --score-test --initial-prompt runs/prompt_02_proposed.txt
```

Test scoring is written to:

```text
runs/test_score.json
```

For traceability, the agent writes JSON artifacts, proposed prompts, and used prompts to `runs/`.

Prompt file meanings:

- `prompt_01_used.txt`: should match `DEFAULT_CLASSIFICATION_PROMPT`.
- `prompt_01_original_proposed.txt`: the first prompt proposed before the review guardrail.
- `prompt_01_proposed.txt`: the final proposed prompt after the review guardrail and optional one-time rewrite. You may edit it, before you type `y` for triggering the next iteration.
- `prompt_02_used.txt`: should match whatever you accepted from `prompt_01_proposed.txt`.

## Current Results

**Accuracy** from the latest local runs:

- Baseline Accuracy (by pure chance): `0.1`.
- `prompt_01_proposed.txt`: validation from iteration 1 = `0.9000`; used in iteration 2 training = `0.9500`.
- `prompt_02_proposed.txt`: validation from iteration 2 = `0.9333`; used in iteration 3 training = `0.9400`.
- `prompt_03_proposed.txt`: validation from iteration 3 = `0.9333`; did not improve over `prompt_02_proposed.txt` on validation.
- Held-out test with `prompt_02_proposed.txt`: `0.9333`.

The best prompt found so far is `prompt_02_proposed.txt`. It achieved validation Accuracy `0.9333` and held-out test Accuracy `0.9333`.

## Files

- `data/banking_complaint_class_keywords.py`: dummy model-derived keyword data for discussion only.
- `data/banking_complaint_training_samples.py`: dummy labelled training set.
- `data/banking_complaint_validation_samples.py`: 30 unique validation samples, one per positive keyword.
- `data/banking_complaint_test_samples.py`: 30 unique test samples, one per positive keyword.
- `src/taxonomy.py`: labels available to the classifier.
- `src/classifier.py`: OpenAI-backed complaint classifier.
- `src/evaluation.py`: confusion matrix and error-case logic.
- `src/optimizer.py`: OpenAI-backed error analysis, prompt rewriting, and prompt review.
- `src/cli.py`: human-in-the-loop iteration runner.

## Token Usage Tracking

While running, the CLI prints an inline classification progress bar:

```text
Classifying [############----------------] 43/100 | requests=43 tokens=18490
```

After each iteration it also prints token usage for:

- classification calls
- error analysis
- prompt improvement
- prompt review
- prompt rewrite, when the review guardrail asks for one
- validation scoring
- iteration total
- full run total

The same token summary is saved into each `runs/iteration_XX.json` artifact.
