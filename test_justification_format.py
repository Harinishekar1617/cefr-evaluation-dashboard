#!/usr/bin/env python3
"""
Test script to demonstrate the new compact justification format.
Shows how the formatting works with sample API responses.
"""

import sys
from pathlib import Path

# Add the cefr_pipeline to the path
sys.path.insert(0, str(Path(__file__).parent))

from cefr_pipeline.assessment import format_justification_compact


def test_v1_detailed_format():
    """Test with v1_detailed prompt response format."""
    sample_response = {
        "cefr_scores": {
            "fluency": "A2",
            "accuracy": "A2",
            "range": "A1",
            "coherence": "A2"
        },
        "overall_level": "A2",
        "key_evidence": {
            "fluency_evidence": "Speech flows naturally with occasional pauses for thinking; uses simple sentences with good pacing",
            "accuracy_errors": [
                "Subject-verb agreement issue: 'the student are'",
                "Missing article: 'I go to school' instead of 'I go to the school'"
            ],
            "range_vocabulary": [
                "uses common verbs: go, see, like, want",
                "basic adjectives: big, small, happy, sad",
                "limited use of complex descriptions"
            ],
            "coherence_structure": "Ideas are clearly organized with simple connectors (and, but); follows a logical sequence"
        }
    }

    print("=" * 70)
    print("V1_DETAILED PROMPT FORMAT")
    print("=" * 70)
    print("\nCompact Justification Output:")
    print(format_justification_compact(sample_response))
    print()


def test_v2_simplified_format():
    """Test with v2_simplified prompt response format."""
    sample_response = {
        "cefr_scores": {
            "fluency": "B1",
            "accuracy": "A2",
            "range": "A2",
            "coherence": "B1"
        },
        "overall_level": "A2",
        "reasoning": {
            "fluency_note": "Student speaks with good flow and minimal hesitation; demonstrates control over simple sentence structures",
            "accuracy_note": "Generally accurate with occasional errors in complex tenses; consistent use of present and past simple",
            "range_note": "Demonstrates vocabulary beyond basic level; uses some varied expressions and descriptive language",
            "coherence_note": "Well-organized response with clear progression; uses linking words effectively"
        }
    }

    print("=" * 70)
    print("V2_SIMPLIFIED PROMPT FORMAT")
    print("=" * 70)
    print("\nCompact Justification Output:")
    print(format_justification_compact(sample_response))
    print()


def test_comparison():
    """Show side-by-side comparison of old vs new format."""
    import json

    sample_response = {
        "cefr_scores": {
            "fluency": "A2",
            "accuracy": "A1",
            "range": "A1",
            "coherence": "A2"
        },
        "overall_level": "A1",
        "key_evidence": {
            "fluency_evidence": "Speech is somewhat hesitant with frequent pauses",
            "accuracy_errors": [
                "Incorrect verb tense: 'I go yesterday'",
                "Missing subject pronoun"
            ],
            "range_vocabulary": ["basic verbs", "common nouns"],
            "coherence_structure": "Very simple organization; minimal use of connectors"
        }
    }

    print("=" * 70)
    print("FORMAT COMPARISON")
    print("=" * 70)

    print("\n❌ OLD FORMAT (Full JSON - Crowded):")
    print("-" * 70)
    print(json.dumps(sample_response, indent=2))

    print("\n✅ NEW FORMAT (Compact - Clean):")
    print("-" * 70)
    print(format_justification_compact(sample_response))
    print()


if __name__ == "__main__":
    test_v1_detailed_format()
    test_v2_simplified_format()
    test_comparison()

    print("=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
