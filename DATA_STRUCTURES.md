# X-Ray Data Structures

## Execution Structure

Top-level object that contains the entire pipeline execution:

```json
{
  "id": "uuid-string",
  "name": "competitor_product_selection",
  "status": "success",
  "timestamp_start": "2025-12-29T10:00:00.000Z",
  "timestamp_end": "2025-12-29T10:00:03.245Z",
  "duration_ms": 3245,
  "tags": {"demo": true, "api": true},
  "steps": [...]
}
```

## Step Structure

Each step in the pipeline:

```json
{
  "id": "uuid-string",
  "name": "apply_filters",
  "type": "filter",
  "status": "success",
  "timestamp_start": "2025-12-29T10:00:01.000Z",
  "timestamp_end": "2025-12-29T10:00:01.250Z",
  "duration_ms": 250,
  "input": {...},
  "output": {...},
  "reasoning": "Applied 3-stage filter...",
  "metadata": {"model": "gpt-4"},
  "evaluations": {...}
}
```

**Key Fields:**
- `type`: llm, api, filter, ranking (for visual categorization)
- `reasoning`: Explains WHY this step made its decisions
- `evaluations`: Large datasets go here (see Evaluation Streaming below)

## Evaluation Structure

For steps that process many items (filtering, scoring, etc.):

```json
{
  "item_id": "B0COMP01",
  "item_data": {
    "title": "HydroFlask 32oz",
    "price": 44.99,
    "rating": 4.5,
    "reviews": 8932
  },
  "checks": [
    {
      "name": "price_range",
      "passed": true,
      "detail": "$44.99 is within $14.99-$59.98"
    },
    {
      "name": "min_rating",
      "passed": true,
      "detail": "4.5 >= 3.8"
    }
  ],
  "qualified": true
}
```

**Key Fields:**
- `item_id`: Unique identifier for the item being evaluated
- `item_data`: Snapshot of the item (so you don't need external lookups)
- `checks`: Array of individual filter/validation results
- `qualified`: Final pass/fail result

## Evaluation Streaming

When a step has many evaluations (e.g., 50+ products), instead of storing them in the execution JSON, we:

1. Write evaluations to a separate JSONL file (one JSON object per line)
2. Store only a summary in the execution JSON:

```json
{
  "evaluations": {
    "mode": "stream",
    "file": "xray_data/evaluations/step-uuid.jsonl",
    "total": 50,
    "passed": 12,
    "failed": 38,
    "pass_rate": 24.0
  }
}
```

**JSONL File Format:**
```
{"item_id": "B0001", "qualified": true, ...}
{"item_id": "B0002", "qualified": false, ...}
{"item_id": "B0003", "qualified": true, ...}
```

**Why?**
- Keeps execution JSON small (KB instead of MB)
- Allows pagination (read only page 1, then page 2 as needed)
- Scales to thousands or millions of items

## Real Example from Demo

**Execution JSON (simplified):**
```json
{
  "id": "abc123",
  "name": "competitor_product_selection",
  "steps": [
    {
      "name": "keyword_generation",
      "input": {"product_title": "Stainless Steel Water Bottle 32oz"},
      "output": {"keywords": ["stainless steel water bottle", "insulated bottle 32oz"]},
      "reasoning": "LLM extracted material, capacity, and feature attributes"
    },
    {
      "name": "apply_filters",
      "input": {"candidates_count": 50},
      "output": {"qualified_count": 12, "failed_count": 38},
      "reasoning": "Applied price, rating, review filters",
      "evaluations": {
        "mode": "stream",
        "file": "xray_data/evaluations/filter-step.jsonl",
        "total": 50,
        "passed": 12
      }
    }
  ]
}
```

**Evaluations JSONL (filter-step.jsonl):**
```jsonl
{"item_id": "B0COMP01", "item_data": {"title": "HydroFlask", "price": 44.99}, "checks": [{"name": "price_range", "passed": true}], "qualified": true}
{"item_id": "B0COMP02", "item_data": {"title": "Generic Bottle", "price": 8.99}, "checks": [{"name": "price_range", "passed": false, "detail": "$8.99 < $12.50 minimum"}], "qualified": false}
```

## Key Design Decisions

**1. Why JSONL instead of JSON array?**
- Can read/write line-by-line without loading entire file
- Easy to append new items
- Natural fit for pagination (read lines 10-20)

**2. Why separate files?**
- Execution JSON stays small (fast to load, parse, display)
- Evaluations loaded only when needed
- Can delete old evaluation files without losing execution history
