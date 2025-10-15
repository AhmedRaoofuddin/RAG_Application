"""
Sanity tests for evaluation metrics math
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from run_eval import EvaluationMetrics


class TestEvaluationMath:
    """Sanity tests for evaluation metric calculations"""

    def test_exact_match_identical(self):
        """Test exact match with identical strings"""
        result = EvaluationMetrics.exact_match("hello world", "hello world")
        assert result == 1.0, "Identical strings should have EM = 1.0"

    def test_exact_match_different(self):
        """Test exact match with different strings"""
        result = EvaluationMetrics.exact_match("hello world", "goodbye world")
        assert result == 0.0, "Different strings should have EM = 0.0"

    def test_exact_match_case_insensitive(self):
        """Test exact match is case insensitive"""
        result = EvaluationMetrics.exact_match("Hello World", "hello world")
        assert result == 1.0, "Should be case insensitive"

    def test_exact_match_whitespace_normalized(self):
        """Test exact match normalizes whitespace"""
        result = EvaluationMetrics.exact_match("  hello world  ", "hello world")
        assert result == 1.0, "Should normalize whitespace"

    def test_f1_identical(self):
        """Test F1 score with identical strings"""
        result = EvaluationMetrics.f1_score("hello world", "hello world")
        assert result == 1.0, "Identical strings should have F1 = 1.0"

    def test_f1_completely_different(self):
        """Test F1 score with completely different strings"""
        result = EvaluationMetrics.f1_score("hello world", "foo bar")
        assert result == 0.0, "Completely different strings should have F1 = 0.0"

    def test_f1_partial_overlap(self):
        """Test F1 score with partial word overlap"""
        result = EvaluationMetrics.f1_score("the quick brown fox", "the quick red fox")

        # Expected: 3 words match (the, quick, fox) out of 4 predicted and 4 expected
        # Precision = 3/4 = 0.75
        # Recall = 3/4 = 0.75
        # F1 = 2 * (0.75 * 0.75) / (0.75 + 0.75) = 0.75

        assert 0.7 <= result <= 0.8, f"F1 should be around 0.75, got {result}"

    def test_f1_one_word_match(self):
        """Test F1 score with one word matching"""
        result = EvaluationMetrics.f1_score("hello world", "hello universe")

        # 1 word matches out of 2
        # Precision = 1/2 = 0.5
        # Recall = 1/2 = 0.5
        # F1 = 2 * (0.5 * 0.5) / (0.5 + 0.5) = 0.5

        assert result == 0.5, f"F1 should be 0.5, got {result}"

    def test_f1_empty_strings(self):
        """Test F1 score with empty strings"""
        result = EvaluationMetrics.f1_score("", "")
        assert result == 0.0, "Empty strings should have F1 = 0.0"

    def test_citation_accuracy_all_present(self):
        """Test citation accuracy when all expected citations are present"""
        predicted = ["doc1.md", "doc2.md", "doc3.md"]
        expected = ["doc1.md", "doc2.md"]

        result = EvaluationMetrics.citation_accuracy(predicted, expected)
        assert result == 1.0, "All expected citations present should give 1.0"

    def test_citation_accuracy_partial(self):
        """Test citation accuracy with partial matches"""
        predicted = ["doc1.md", "doc3.md"]
        expected = ["doc1.md", "doc2.md"]

        result = EvaluationMetrics.citation_accuracy(predicted, expected)
        assert result == 0.5, "1 of 2 citations should give 0.5"

    def test_citation_accuracy_none_present(self):
        """Test citation accuracy with no matches"""
        predicted = ["doc3.md", "doc4.md"]
        expected = ["doc1.md", "doc2.md"]

        result = EvaluationMetrics.citation_accuracy(predicted, expected)
        assert result == 0.0, "No matches should give 0.0"

    def test_citation_accuracy_empty_expected(self):
        """Test citation accuracy with no expected citations"""
        predicted = ["doc1.md"]
        expected = []

        result = EvaluationMetrics.citation_accuracy(predicted, expected)
        assert result == 1.0, "No expected citations should give 1.0"

    def test_citation_accuracy_substring_match(self):
        """Test citation accuracy with substring matching"""
        predicted = ["01_fortes_eduction_overview.md"]
        expected = ["overview.md"]

        result = EvaluationMetrics.citation_accuracy(predicted, expected)
        # Should match because expected is substring of predicted
        assert result == 1.0, "Substring match should count"

    def test_normalize_text(self):
        """Test text normalization"""
        tests = [
            ("  Hello World  ", "hello world"),
            ("UPPERCASE", "uppercase"),
            ("MiXeD CaSe", "mixed case"),
            ("  extra   spaces  ", "extra   spaces"),
        ]

        for input_text, expected in tests:
            result = EvaluationMetrics.normalize_text(input_text)
            assert result == expected, f"Normalization failed for '{input_text}'"

    def test_f1_precision_recall_calculation(self):
        """Test F1 calculation logic step by step"""
        predicted = "apple banana cherry"
        expected = "apple banana date"

        # Manually calculate
        pred_words = set(predicted.lower().split())  # {apple, banana, cherry}
        exp_words = set(expected.lower().split())    # {apple, banana, date}

        true_positive = len(pred_words.intersection(exp_words))  # {apple, banana} = 2
        precision = true_positive / len(pred_words)  # 2/3 = 0.666...
        recall = true_positive / len(exp_words)      # 2/3 = 0.666...
        expected_f1 = 2 * (precision * recall) / (precision + recall)  # 0.666...

        result = EvaluationMetrics.f1_score(predicted, expected)

        assert abs(result - expected_f1) < 0.01, f"F1 calculation mismatch: {result} vs {expected_f1}"


def test_all_metrics_integration():
    """Integration test for all metrics"""
    # Test case: similar but not identical answers
    predicted = "Fortes Eduction is an advanced RAG system for Q&A"
    expected = "Fortes Eduction is a RAG system for question answering"

    em = EvaluationMetrics.exact_match(predicted, expected)
    f1 = EvaluationMetrics.f1_score(predicted, expected)

    # Should not be exact match
    assert em == 0.0, "Should not be exact match"

    # But should have good F1 (many words overlap)
    assert f1 > 0.5, f"Should have good F1 score, got {f1}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

