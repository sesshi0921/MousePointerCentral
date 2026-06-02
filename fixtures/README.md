# Fixture Data

This directory contains screenshot fixtures and ground-truth labels
for evaluating the screen-perception pipeline (§10).

## Structure

```
fixtures/
  screenshots/          # Real application screenshots (PNG)
  labels/               # JSON label files (one per screenshot)
  evaluate.py           # Evaluation harness
```

## Label format

Each label file is a JSON array of ground-truth elements:

```json
[
  {
    "id": "gt_001",
    "type": "button",
    "text": "Save",
    "bounds": [120, 340, 220, 380]
  }
]
```

## Metrics

- **Recall** (操作対象の取りこぼし率): ground-truth elements matched by candidates.
- **Click success rate**: final `screen` coordinates land inside the correct element bounds.

## Completion criteria (provisional)

- Click success rate ≥ 90%
- Recall ≥ 95%

Values are provisional and will be finalised after the first measurement run.
