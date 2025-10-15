# Evaluation System

## Overview

Fortes Education includes a comprehensive evaluation harness to measure and track RAG system performance.

## Metrics

### Exact Match (EM)

**Definition**: Percentage of answers that exactly match the expected answer (case-insensitive, whitespace-normalized).

**Formula**: `EM = (Exact Matches / Total Questions) × 100`

**Range**: 0% to 100%

**Use Case**: Strict evaluation for factual questions with definitive answers.

### F1 Score

**Definition**: Harmonic mean of precision and recall at the word level.

**Formula**: 
```
Precision = (True Positive Words / Predicted Words)
Recall = (True Positive Words / Expected Words)
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Range**: 0.0 to 1.0

**Use Case**: Flexible evaluation that allows partial matches.

### Semantic Similarity

**Definition**: Cosine similarity between embedding vectors of predicted and expected answers.

**Range**: 0.0 to 1.0

**Use Case**: Evaluate semantic equivalence even when wording differs.

### Citation Accuracy

**Definition**: Percentage of expected citations that appear in the response.

**Formula**: `Citation Accuracy = (Correct Citations / Expected Citations) × 100`

**Range**: 0% to 100%

**Use Case**: Verify attribution and source tracking.

## Evaluation Configuration

### eval.yaml Format

```yaml
evaluation_set:
  - question: "What is Fortes Education?"
    expected_answer: "Fortes Education is an advanced RAG Q&A system"
    expected_citations: ["01_fortes_eduction_overview.md"]
    metadata:
      category: "overview"
      difficulty: "easy"
  
  - question: "How do I install the system?"
    expected_answer: "Clone the repository, install dependencies, configure environment"
    expected_citations: ["02_installation_guide.md"]
    metadata:
      category: "installation"
      difficulty: "medium"
```

### Running Evaluations

#### Command Line

```bash
# Backend evaluation
python backend/run_eval.py

# With custom eval file
python backend/run_eval.py --eval-file custom_eval.yaml
```

#### Output

Results are written to `eval_report.json`:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "total_questions": 15,
  "metrics": {
    "exact_match": 0.73,
    "f1_score": 0.85,
    "semantic_similarity": 0.88,
    "citation_accuracy": 0.80
  },
  "results": [
    {
      "question": "What is Fortes Education?",
      "predicted": "Fortes Education is an advanced RAG system...",
      "expected": "Fortes Education is an advanced RAG Q&A system",
      "em": 0,
      "f1": 0.89,
      "similarity": 0.95,
      "citation_match": 1.0
    }
  ]
}
```

## Evaluation Categories

### Accuracy Tests

Measure correctness of answers:
- Factual questions
- Definition queries
- Numerical answers

### Attribution Tests

Verify citation system:
- Citation presence
- Citation accuracy
- Line number correctness

### Guardrail Tests

Ensure safety features work:
- Prompt injection blocking
- PII redaction
- Low-grounding refusals

### Performance Tests

Measure system efficiency:
- Response latency
- Token usage
- Cache hit rate

## Continuous Evaluation

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/eval.yml
name: Evaluation
on: [push, pull_request]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run evaluation
        run: python backend/run_eval.py
      - name: Check thresholds
        run: |
          python backend/check_eval_thresholds.py \
            --min-f1 0.75 \
            --min-similarity 0.80
```

### Regression Detection

Track metrics over time:

```python
# Compare current eval to baseline
if current_f1 < baseline_f1 - 0.05:
    print("WARNING: F1 score regression detected!")
    exit(1)
```

## Best Practices

1. **Diverse Test Set**: Include questions of varying difficulty and topics
2. **Regular Updates**: Update eval set when adding new documents
3. **Threshold Tuning**: Set realistic thresholds based on your requirements
4. **Track Trends**: Monitor metrics over time, not just absolute values
5. **Document Edge Cases**: Add failing cases to eval set for regression prevention

## Sample Evaluation Set

The default `eval.yaml` includes:
- 15 Q&A pairs
- Coverage of all major topics
- Mix of easy, medium, and hard questions
- Various citation requirements
- Guardrail test cases

## Interpreting Results

### Good Performance

- EM: > 70%
- F1: > 0.80
- Similarity: > 0.85
- Citation: > 75%

### Acceptable Performance

- EM: 50-70%
- F1: 0.70-0.80
- Similarity: 0.75-0.85
- Citation: 60-75%

### Needs Improvement

- EM: < 50%
- F1: < 0.70
- Similarity: < 0.75
- Citation: < 60%

If performance is below acceptable, consider:
- Adding more/better documents
- Tuning chunking parameters
- Adjusting retrieval settings
- Improving prompts

