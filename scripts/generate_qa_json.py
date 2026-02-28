#!/usr/bin/env python3
"""GAP-510: Generate static JSON from questionnaire Markdown files for the trust center.

Parses all questionnaire/*.md files and outputs a JSON array suitable for
client-side search in the trust.aumos.ai Fuse.js search component.

Usage:
    python scripts/generate_qa_json.py --output trust-center/questionnaire-data.json

The output JSON is a flat array of objects:
    [{"question": "...", "answer": "...", "category": "...", "id": "..."}]
"""
from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path

import click


QUESTIONNAIRE_DIR = Path(__file__).parent.parent / "questionnaire"
QUESTION_PATTERN = re.compile(r"^\*\*Q:\s*(.+?)\*\*$", re.MULTILINE)
CATEGORY_PATTERN = re.compile(r"^##\s+(?:Category:\s+)?(.+)$", re.MULTILINE)


def _parse_questionnaire_file(md_file: Path) -> list[dict[str, str]]:
    """Parse a single questionnaire Markdown file into Q&A pairs.

    Args:
        md_file: Path to the questionnaire Markdown file.

    Returns:
        List of Q&A dicts with question, answer, category, id.
    """
    content = md_file.read_text(encoding="utf-8")
    paragraphs = content.split("\n\n")
    qa_pairs: list[dict[str, str]] = []
    current_category = md_file.stem.replace("-", " ").title()

    for i, paragraph in enumerate(paragraphs):
        stripped = paragraph.strip()

        # Check for category header (## Category: Name or ## Name)
        cat_match = CATEGORY_PATTERN.search(stripped)
        if cat_match and stripped.startswith("##"):
            category_text = cat_match.group(1).strip()
            if category_text.lower().startswith("category:"):
                category_text = category_text[len("category:"):].strip()
            current_category = category_text
            continue

        # Check for question
        q_match = QUESTION_PATTERN.search(stripped)
        if q_match and i + 1 < len(paragraphs):
            question_text = q_match.group(1).strip()
            answer_text = paragraphs[i + 1].strip()

            # Skip if answer is another question (malformed — missing answer)
            if QUESTION_PATTERN.search(answer_text):
                continue

            # Skip empty answers
            if not answer_text:
                continue

            qa_pairs.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, question_text)),
                "question": question_text,
                "answer": answer_text,
                "category": current_category,
                "source": md_file.name,
            })

    return qa_pairs


def generate_qa_json(questionnaire_dir: Path) -> list[dict[str, str]]:
    """Parse all questionnaire files and return a combined Q&A list.

    Args:
        questionnaire_dir: Directory containing questionnaire Markdown files.

    Returns:
        Combined list of all Q&A pairs from all files.
    """
    all_pairs: list[dict[str, str]] = []

    for md_file in sorted(questionnaire_dir.glob("*.md")):
        pairs = _parse_questionnaire_file(md_file)
        all_pairs.extend(pairs)

    return all_pairs


@click.command()
@click.option(
    "--output",
    "output_path",
    default="-",
    type=click.Path(),
    help="Output JSON file path (default: stdout).",
)
@click.option(
    "--questionnaire-dir",
    "questionnaire_dir",
    default=str(QUESTIONNAIRE_DIR),
    type=click.Path(exists=True),
    help=f"Directory containing questionnaire Markdown files (default: {QUESTIONNAIRE_DIR}).",
)
@click.option(
    "--pretty",
    is_flag=True,
    default=False,
    help="Pretty-print JSON output.",
)
def main(output_path: str, questionnaire_dir: str, pretty: bool) -> None:
    """Generate a static JSON file from questionnaire Markdown for the trust center.

    Parses all questionnaire/*.md files and outputs JSON suitable for
    Fuse.js client-side search on trust.aumos.ai.

    Args:
        output_path: Path to write JSON output, or '-' for stdout.
        questionnaire_dir: Override questionnaire directory path.
        pretty: Pretty-print the JSON output.
    """
    qa_pairs = generate_qa_json(Path(questionnaire_dir))

    if not qa_pairs:
        click.echo(
            f"WARNING: No Q&A pairs found in {questionnaire_dir}.",
            err=True,
        )

    click.echo(f"Generated {len(qa_pairs)} Q&A pairs.", err=True)

    json_output = json.dumps(
        qa_pairs,
        indent=2 if pretty else None,
        ensure_ascii=False,
    )

    if output_path == "-":
        click.echo(json_output)
    else:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json_output, encoding="utf-8")
        click.echo(f"Written: {output_file} ({len(qa_pairs)} entries)", err=True)


if __name__ == "__main__":
    main()
