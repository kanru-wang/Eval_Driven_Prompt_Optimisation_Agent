# Eval Driven Prompt Optimisation Agent

This project is a small prototype for iterative LLM-based text classification.
It classifies retail banking complaints, evaluates confusion patterns, asks an
OpenAI model to analyse the errors, proposes a better classification prompt, and
waits for human approval before running the next iteration.

## Important Boundary

The classifier sees:

- the complaint text
- the allowed class labels
- the current classification prompt

The classifier does not see:

- `banking_complaint_class_keywords.py`
- the sample's ground-truth label during classification

Ground-truth labels from `banking_complaint_samples.py` are only used after
prediction to build the confusion matrix and error cases.

## Setup

```bash
pip install -e .
```

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

Or without installing the console script:

```bash
python -m promptopt_agent.cli --iterations 3
```

To resume later from a saved prompt file, pass `--initial-prompt`:

```bash
promptopt-agent --initial-prompt runs/prompt_01_proposed.txt --iterations 2
```

At the end of each iteration, review the proposed prompt file:

```text
runs/prompt_01_proposed.txt
```

You can edit and save that file before answering the terminal prompt. If you
type `y`, the agent reloads the saved file and uses that reviewed prompt for the
next classification/evaluation loop.

The agent writes JSON artifacts, proposed prompts, and used prompts to `runs/`.
For traceability, each iteration keeps both sides of the prompt handoff:

```text
runs/prompt_01_used.txt
runs/prompt_01_proposed.txt
runs/prompt_02_used.txt
runs/prompt_02_proposed.txt
```

Prompt file meanings:

- `prompt_01_used.txt`: should match `DEFAULT_CLASSIFICATION_PROMPT`.
- `prompt_01_proposed.txt`: should be the first improved version.
- `prompt_02_used.txt`: should match whatever you accepted from `prompt_01_proposed.txt`.

## Files

- `banking_complaint_class_keywords.py`: dummy model-derived keyword data for discussion only.
- `banking_complaint_samples.py`: dummy labelled evaluation set.
- `src/promptopt_agent/taxonomy.py`: labels available to the classifier.
- `src/promptopt_agent/classifier.py`: OpenAI-backed complaint classifier.
- `src/promptopt_agent/evaluation.py`: confusion matrix and error-case logic.
- `src/promptopt_agent/optimizer.py`: OpenAI-backed error analysis and prompt rewriting.
- `src/promptopt_agent/cli.py`: human-in-the-loop iteration runner.

## Token Usage Tracking

While running, the CLI prints an inline classification progress bar:

```text
Classifying [############----------------] 43/100 | requests=43 tokens=18490
```

After each iteration it also prints token usage for:

- classification calls
- error analysis
- prompt improvement
- iteration total
- full run total

The same token summary is saved into each `runs/iteration_XX.json` artifact.
