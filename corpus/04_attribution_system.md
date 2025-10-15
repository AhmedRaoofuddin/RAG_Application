# Attribution and Hallucination Detection

## Overview

Fortes Education implements sentence-level attribution to ensure every claim in generated responses is traceable to source documents.

## How Attribution Works

### Sentence-Level Citations

Each sentence in a generated response is mapped to one or more supporting chunks from the knowledge base:

1. **Response Parsing**: The generated answer is split into individual sentences
2. **Similarity Matching**: Each sentence is compared against retrieved chunks
3. **Citation Assignment**: Chunks with similarity above threshold are assigned as citations
4. **Confidence Scoring**: Each sentence receives a confidence score based on support strength

### Citation Format

Citations appear in two ways:

**In-text**: `[citation:1][citation:2]`
**Detailed view**: Shows document ID, line numbers, and similarity scores

Example:
```
Document: installation_guide.md
Lines: 15-23
Similarity: 0.87
Preview: "Navigate to the backend directory and install..."
```

## Hallucination Detection

### Definition

A hallucination occurs when the system generates a claim not supported by retrieved knowledge base content.

### Detection Method

1. For each sentence, find supporting chunks
2. If similarity score < threshold (default: 0.65), mark as unsupported
3. If number of supporting citations < minimum (default: 1), flag as hallucination

### Visual Indicators

Unsupported sentences receive special markers:

- **Red "Unsupported" chip**: Appears next to flagged sentences
- **Warning icon**: Visual indicator of potential hallucination
- **Lower confidence score**: Numerical confidence displayed

### Hallucination Statistics

The system tracks:
- Total sentences in response
- Number of supported sentences
- Number of unsupported sentences
- Hallucination rate (percentage)
- Average confidence across all sentences

## Configuration

### Citation Threshold

Adjust the minimum similarity for citation support:

```python
CITATION_THRESHOLD = 0.65  # 0.0 to 1.0
```

Lower values = more lenient (more citations assigned)
Higher values = stricter (fewer citations, more hallucinations flagged)

### Minimum Citations

Set minimum number of supporting citations per sentence:

```python
MIN_CITATIONS = 1
```

## Best Practices

1. **Review flagged content**: Always check sentences marked as unsupported
2. **Improve knowledge base**: Add missing documents if hallucinations are frequent
3. **Tune thresholds**: Balance between over-flagging and under-flagging
4. **Use citations**: Encourage users to click citations to verify claims

## Example Output

```json
{
  "sentences": [
    {
      "text": "Fortes Education supports PDF, DOCX, and Markdown formats.",
      "citations": [
        {
          "doc_id": "01_fortes_eduction_overview.md",
          "line_range": "10-12",
          "similarity": 0.92
        }
      ],
      "is_supported": true,
      "confidence": 0.92,
      "hallucination_flag": false
    },
    {
      "text": "The system can process 1000 documents per second.",
      "citations": [],
      "is_supported": false,
      "confidence": 0.0,
      "hallucination_flag": true
    }
  ],
  "has_hallucination": true
}
```

