#!/usr/bin/env python3
"""GAP-512: Batch-answer a customer security questionnaire using semantic matching.

Loads the AumOS Q&A database from questionnaire/ Markdown files and uses
sentence-transformers to semantically match each question in a customer
questionnaire CSV to the best matching pre-answered question.

Usage:
    python scripts/answer_questionnaire.py \\
        --input customer-questionnaire.csv \\
        --output answers.csv \\
        --threshold 0.75

Input CSV format:
    question,[any other columns]
    "Do you encrypt data at rest?","..."
    "What is your incident response time?","..."

Output CSV: adds matched_question, answer, confidence, category columns.

Requirements:
    pip install sentence-transformers pandas

Environment:
    AUMOS_QA_DIR — Override questionnaire directory (default: questionnaire/)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

import click


QUESTIONNAIRE_DIR = Path(os.environ.get(
    "AUMOS_QA_DIR",
    str(Path(__file__).parent.parent / "questionnaire"),
))
MODEL_NAME = "all-mpnet-base-v2"


def _load_qa_database(questionnaire_dir: Path) -> list[dict[str, str]]:
    """Load all Q&A pairs from questionnaire Markdown files.

    Parses Markdown files in the questionnaire directory. Expected format:

        ## Category: General Security

        **Q: Do you encrypt data at rest?**
        Yes, AumOS encrypts all data at rest using AES-256...

    Args:
        questionnaire_dir: Path to the directory containing Markdown Q&A files.

    Returns:
        List of dicts with 'question', 'answer', and 'category' keys.
    """
    qa_pairs: list[dict[str, str]] = []
    current_category = "General"

    question_pattern = re.compile(r"^\*\*Q:\s*(.+?)\*\*$", re.MULTILINE)
    category_pattern = re.compile(r"^##\s+Category:\s+(.+)$", re.MULTILINE)

    for md_file in sorted(questionnaire_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        paragraphs = content.split("\n\n")

        for i, paragraph in enumerate(paragraphs):
            # Check for category header
            cat_match = category_pattern.search(paragraph)
            if cat_match:
                current_category = cat_match.group(1).strip()
                continue

            # Check for question
            q_match = question_pattern.search(paragraph)
            if q_match and i + 1 < len(paragraphs):
                question_text = q_match.group(1).strip()
                answer_text = paragraphs[i + 1].strip()

                # Skip if answer is another question (malformed input)
                if question_pattern.search(answer_text):
                    continue

                qa_pairs.append({
                    "question": question_text,
                    "answer": answer_text,
                    "category": current_category,
                    "source": md_file.name,
                })

    return qa_pairs


def answer_questionnaire(
    input_path: str,
    output_path: str,
    threshold: float = 0.75,
    model_name: str = MODEL_NAME,
) -> None:
    """Batch-answer a customer questionnaire using semantic matching.

    Args:
        input_path: Path to input CSV with a 'question' column.
        output_path: Path to write output CSV with answers appended.
        threshold: Minimum cosine similarity score to accept a match.
        model_name: Sentence-transformers model to use for embeddings.
    """
    try:
        import pandas as pd
        from sentence_transformers import SentenceTransformer, util
    except ImportError as exc:
        click.echo(
            f"ERROR: Missing dependency: {exc}. "
            "Install with: pip install sentence-transformers pandas",
            err=True,
        )
        sys.exit(1)

    # Load Q&A database
    click.echo(f"Loading Q&A database from {QUESTIONNAIRE_DIR}...", err=True)
    qa_db = _load_qa_database(QUESTIONNAIRE_DIR)
    if not qa_db:
        click.echo(
            f"ERROR: No Q&A pairs found in {QUESTIONNAIRE_DIR}. "
            "Check that questionnaire/ directory contains Markdown files with "
            "**Q: question** format.",
            err=True,
        )
        sys.exit(1)
    click.echo(f"Loaded {len(qa_db)} Q&A pairs.", err=True)

    # Load customer questionnaire
    df = pd.read_csv(input_path)
    if "question" not in df.columns:
        click.echo(
            "ERROR: Input CSV must have a 'question' column.",
            err=True,
        )
        sys.exit(1)
    click.echo(f"Loaded {len(df)} customer questions.", err=True)

    # Encode the Q&A database
    click.echo(f"Loading embedding model '{model_name}' (may download on first run)...", err=True)
    model = SentenceTransformer(model_name)

    click.echo("Encoding Q&A database...", err=True)
    qa_questions = [item["question"] for item in qa_db]
    qa_embeddings = model.encode(qa_questions, show_progress_bar=False)

    # Match each customer question
    click.echo("Matching customer questions...", err=True)
    matched_questions: list[str | None] = []
    answers: list[str] = []
    confidences: list[float] = []
    categories: list[str | None] = []

    customer_embeddings = model.encode(
        df["question"].tolist(), show_progress_bar=True
    )

    for i, query_embedding in enumerate(customer_embeddings):
        scores = util.cos_sim(query_embedding, qa_embeddings)[0]
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        if best_score >= threshold:
            best_match = qa_db[best_idx]
            matched_questions.append(best_match["question"])
            answers.append(best_match["answer"])
            confidences.append(round(best_score, 4))
            categories.append(best_match["category"])
        else:
            matched_questions.append(None)
            answers.append("NEEDS MANUAL REVIEW — no confident match found")
            confidences.append(round(best_score, 4))
            categories.append(None)

    # Write output
    df["matched_question"] = matched_questions
    df["answer"] = answers
    df["confidence"] = confidences
    df["category"] = categories
    df.to_csv(output_path, index=False)

    auto_answered = sum(1 for c in confidences if c >= threshold)
    needs_review = len(confidences) - auto_answered
    click.echo(f"\nResults written to: {output_path}")
    click.echo(f"  Auto-answered: {auto_answered}/{len(df)} ({100 * auto_answered // len(df)}%)")
    click.echo(f"  Needs review:  {needs_review}/{len(df)}")
    click.echo(f"  Threshold used: {threshold}")


@click.command()
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="Input CSV file with a 'question' column.",
)
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(),
    help="Output CSV file path.",
)
@click.option(
    "--threshold",
    default=0.75,
    type=float,
    show_default=True,
    help="Minimum cosine similarity score to auto-answer (0.0-1.0).",
)
@click.option(
    "--model",
    "model_name",
    default=MODEL_NAME,
    show_default=True,
    help="Sentence-transformers model name.",
)
def main(input_path: str, output_path: str, threshold: float, model_name: str) -> None:
    """Batch-answer a customer security questionnaire using semantic similarity.

    Matches each question in the input CSV against the AumOS Q&A database
    using sentence-transformers embeddings. Questions without a confident
    match are flagged for manual review.

    Args:
        input_path: Path to customer questionnaire CSV.
        output_path: Path to write answers CSV.
        threshold: Similarity threshold for accepting a match.
        model_name: Sentence-transformers model identifier.
    """
    answer_questionnaire(input_path, output_path, threshold, model_name)


if __name__ == "__main__":
    main()
