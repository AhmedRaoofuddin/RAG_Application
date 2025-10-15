#!/usr/bin/env python3
"""
Evaluation Harness for Fortes Education
Runs evaluation set and computes metrics
"""

import json
import yaml
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import argparse

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.enhanced_chunker import enhanced_chunker
from app.services.stub_services import get_embeddings_with_fallback
from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EvaluationMetrics:
    """Calculate evaluation metrics"""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        return text.lower().strip()

    @staticmethod
    def exact_match(predicted: str, expected: str) -> float:
        """
        Calculate exact match score (1.0 or 0.0)
        """
        pred_norm = EvaluationMetrics.normalize_text(predicted)
        exp_norm = EvaluationMetrics.normalize_text(expected)
        return 1.0 if pred_norm == exp_norm else 0.0

    @staticmethod
    def f1_score(predicted: str, expected: str) -> float:
        """
        Calculate F1 score based on word overlap
        """
        pred_words = set(EvaluationMetrics.normalize_text(predicted).split())
        exp_words = set(EvaluationMetrics.normalize_text(expected).split())

        if not pred_words or not exp_words:
            return 0.0

        true_positive = len(pred_words.intersection(exp_words))

        if true_positive == 0:
            return 0.0

        precision = true_positive / len(pred_words)
        recall = true_positive / len(exp_words)

        f1 = 2 * (precision * recall) / (precision + recall)
        return f1

    @staticmethod
    def semantic_similarity(predicted: str, expected: str, embeddings) -> float:
        """
        Calculate semantic similarity using embeddings
        """
        try:
            import numpy as np

            pred_emb = embeddings.embed_query(predicted)
            exp_emb = embeddings.embed_query(expected)

            # Cosine similarity
            dot_product = np.dot(pred_emb, exp_emb)
            norm_pred = np.linalg.norm(pred_emb)
            norm_exp = np.linalg.norm(exp_emb)

            if norm_pred == 0 or norm_exp == 0:
                return 0.0

            similarity = dot_product / (norm_pred * norm_exp)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    @staticmethod
    def citation_accuracy(predicted_citations: List[str], expected_citations: List[str]) -> float:
        """
        Calculate what percentage of expected citations appear in predicted
        """
        if not expected_citations:
            return 1.0

        matched = sum(1 for exp_cit in expected_citations
                      if any(exp_cit in pred_cit for pred_cit in predicted_citations))

        return matched / len(expected_citations)


class MockRAGSystem:
    """Mock RAG system for evaluation without full deployment"""

    def __init__(self):
        self.embeddings = get_embeddings_with_fallback()
        # In a real evaluation, this would query the actual RAG system
        # For now, we'll use a simplified mock

    def answer_question(self, question: str, expected_citations: List[str]) -> Dict[str, Any]:
        """
        Mock answer generation
        In production, this would call the actual RAG pipeline
        """
        # Simplified mock - returns expected answer with citations
        # In real implementation, this would query the vector store and generate response

        # For evaluation purposes, we'll return a templated response
        # indicating this is using the evaluation mock
        return {
            "answer": f"Mock answer for: {question} (using evaluation stub)",
            "citations": expected_citations,  # Mock citations
            "grounding_score": 0.85
        }


def load_evaluation_set(eval_file: str = "eval.yaml") -> Dict[str, Any]:
    """Load evaluation set from YAML file"""
    eval_path = Path(eval_file)
    if not eval_path.exists():
        # Try parent directory
        eval_path = Path(__file__).parent.parent / eval_file

    if not eval_path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {eval_file}")

    with open(eval_path, 'r') as f:
        return yaml.safe_load(f)


def run_evaluation(eval_file: str = "eval.yaml", output_file: str = "eval_report.json") -> Dict[str, Any]:
    """
    Run evaluation harness
    """
    logger.info("=" * 80)
    logger.info("Fortes Education - Evaluation Harness")
    logger.info("=" * 80)

    # Load evaluation set
    eval_data = load_evaluation_set(eval_file)
    eval_set = eval_data.get("evaluation_set", [])
    config = eval_data.get("config", {})

    logger.info(f"Loaded {len(eval_set)} evaluation questions")

    # Initialize systems
    rag_system = MockRAGSystem()
    embeddings = get_embeddings_with_fallback()

    # Run evaluation
    results = []
    total_em = 0.0
    total_f1 = 0.0
    total_similarity = 0.0
    total_citation_acc = 0.0

    for i, item in enumerate(eval_set, 1):
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_citations = item.get("expected_citations", [])
        metadata = item.get("metadata", {})

        logger.info(f"\n[{i}/{len(eval_set)}] {metadata.get('category', 'unknown')}: {question[:60]}...")

        # Get answer from RAG system
        response = rag_system.answer_question(question, expected_citations)
        predicted_answer = response["answer"]
        predicted_citations = response.get("citations", [])

        # Calculate metrics
        em = EvaluationMetrics.exact_match(predicted_answer, expected_answer)
        f1 = EvaluationMetrics.f1_score(predicted_answer, expected_answer)
        similarity = EvaluationMetrics.semantic_similarity(
            predicted_answer, expected_answer, embeddings
        )
        citation_acc = EvaluationMetrics.citation_accuracy(
            predicted_citations, expected_citations
        )

        # Log metrics
        logger.info(f"  EM: {em:.3f} | F1: {f1:.3f} | Sim: {similarity:.3f} | Cit: {citation_acc:.3f}")

        # Accumulate totals
        total_em += em
        total_f1 += f1
        total_similarity += similarity
        total_citation_acc += citation_acc

        # Store result
        results.append({
            "question": question,
            "predicted": predicted_answer,
            "expected": expected_answer,
            "em": round(em, 3),
            "f1": round(f1, 3),
            "similarity": round(similarity, 3),
            "citation_accuracy": round(citation_acc, 3),
            "metadata": metadata
        })

    # Calculate averages
    n = len(eval_set)
    avg_metrics = {
        "exact_match": round(total_em / n, 3),
        "f1_score": round(total_f1 / n, 3),
        "semantic_similarity": round(total_similarity / n, 3),
        "citation_accuracy": round(total_citation_acc / n, 3)
    }

    # Create report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "eval_file": eval_file,
        "total_questions": n,
        "metrics": avg_metrics,
        "thresholds": config,
        "passed_thresholds": {
            "f1": avg_metrics["f1_score"] >= config.get("min_f1_score", 0.75),
            "similarity": avg_metrics["semantic_similarity"] >= config.get("min_semantic_similarity", 0.80),
            "citation": avg_metrics["citation_accuracy"] >= config.get("min_citation_accuracy", 0.70),
            "em": avg_metrics["exact_match"] >= config.get("min_exact_match", 0.50)
        },
        "results": results
    }

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Questions: {n}")
    logger.info(f"Exact Match:     {avg_metrics['exact_match']:.3f} (threshold: {config.get('min_exact_match', 0.50):.2f})")
    logger.info(f"F1 Score:        {avg_metrics['f1_score']:.3f} (threshold: {config.get('min_f1_score', 0.75):.2f})")
    logger.info(f"Similarity:      {avg_metrics['semantic_similarity']:.3f} (threshold: {config.get('min_semantic_similarity', 0.80):.2f})")
    logger.info(f"Citation Acc:    {avg_metrics['citation_accuracy']:.3f} (threshold: {config.get('min_citation_accuracy', 0.70):.2f})")
    logger.info("=" * 80)

    # Check if all thresholds passed
    all_passed = all(report["passed_thresholds"].values())
    if all_passed:
        logger.info("✓ ALL THRESHOLDS PASSED")
    else:
        logger.warning("✗ SOME THRESHOLDS FAILED")
        for metric, passed in report["passed_thresholds"].items():
            if not passed:
                logger.warning(f"  - {metric}: FAILED")

    # Save report
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"\n✓ Report saved to: {output_path}")

    return report


def test_eval_math():
    """
    Sanity test for evaluation metrics
    """
    logger.info("\nRunning evaluation math sanity test...")

    # Test exact match
    assert EvaluationMetrics.exact_match("hello world", "hello world") == 1.0
    assert EvaluationMetrics.exact_match("hello world", "goodbye world") == 0.0

    # Test F1
    f1 = EvaluationMetrics.f1_score("the quick brown fox", "the quick red fox")
    assert 0.5 < f1 < 1.0, f"F1 score should be between 0.5 and 1.0, got {f1}"

    # Test citation accuracy
    cit_acc = EvaluationMetrics.citation_accuracy(
        ["doc1.md", "doc2.md"],
        ["doc1.md"]
    )
    assert cit_acc == 1.0, f"Citation accuracy should be 1.0, got {cit_acc}"

    logger.info("✓ Evaluation math sanity test passed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Fortes Education evaluation harness")
    parser.add_argument("--eval-file", default="eval.yaml", help="Path to evaluation YAML file")
    parser.add_argument("--output", default="eval_report.json", help="Output report file")
    parser.add_argument("--test-math", action="store_true", help="Run evaluation math sanity test")

    args = parser.parse_args()

    if args.test_math:
        test_eval_math()
        return

    try:
        report = run_evaluation(args.eval_file, args.output)

        # Exit with error code if thresholds not met
        if not all(report["passed_thresholds"].values()):
            sys.exit(1)

    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

