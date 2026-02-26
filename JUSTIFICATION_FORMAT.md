# Justification Format Changes

## Overview
The justification output has been restructured to be less crowded and more readable. Instead of showing the entire JSON response with repeated CEFR scores, the output now focuses on evidence organized by parameter.

## New Format (Compact)
The justification column now displays evidence-based reasoning for each parameter:

```
• Fluency: Speech flows naturally with occasional pauses for thinking; uses simple sentences with good pacing
• Accuracy: Mostly correct grammar with minor errors in past tense conjugation; articles are used correctly
• Range: Limited vocabulary but consistent use of common verbs and basic adjectives; struggles with more complex descriptors
• Coherence: Ideas are clearly organized with simple connectors; follows a logical sequence
```

### Benefits
- **Less crowded**: No repeated CEFR scores
- **Organized by parameter**: Each dimension has its own bullet point
- **Evidence-based**: Shows the reasoning behind each score
- **Includes examples**: When available, includes quotes or specific examples from the transcript

## Old Format (Full JSON)
If you need the complete API response with all details, you can switch back to the full format by modifying the code:

In `cefr_pipeline/assessment.py`, change:
```python
'justification': format_justification_for_storage(result, format_type="compact")
```

To:
```python
'justification': format_justification_for_storage(result, format_type="full")
```

The full format returns the complete JSON response from the API:
```json
{
  "cefr_scores": {
    "fluency": "A2",
    "accuracy": "A2",
    "range": "A1",
    "coherence": "A2"
  },
  "overall_level": "A2",
  "key_evidence": {
    "fluency_evidence": "...",
    "accuracy_errors": [...],
    "range_vocabulary": [...],
    "coherence_structure": "..."
  }
}
```

## Implementation Details

### How It Works
1. When the API returns a response, `evaluate_student_dialogue()` extracts scores and calls `format_justification_for_storage()`
2. `format_justification_compact()` extracts evidence from the API response's `key_evidence` or `reasoning` sections
3. Evidence is formatted as bullet points organized by parameter (fluency, accuracy, range, coherence)
4. The formatted string is stored in the `justification` column

### Supported Formats
- **v1_detailed prompt**: Extracts from `key_evidence` section
- **v2_simplified prompt**: Extracts from `reasoning` section
- **Custom prompts**: As long as they return JSON with evidence/reasoning sections, the formatter will adapt

## Excel & CSV Output
The compact format is automatically applied to all output:
- **Individual Turns sheet**: Each row shows compact justification
- **Individual Turns CSV**: Same compact format
- **Aggregated results**: No justification (only aggregated scores)

## Reverting to Full Format
To switch back to full format output:
1. Edit `cefr_pipeline/assessment.py`
2. Find the `format_justification_for_storage()` calls (lines 176 and 186)
3. Change `format_type="compact"` to `format_type="full"`
4. Re-run your evaluations

Note: You cannot convert existing compact format back to full format, as the compact format discards some JSON information.
