# metadata_generator.py

import os
import json
from typing import Any, Dict

from data_utils import extract_text, get_file_metadata
from nlp_utils import (
    extract_keywords,
    extract_summary,
    extract_entities,
    extract_sections,    # ← NEW
)
from langdetect import detect


def _detect_title(text: str, max_words: int = 20) -> str:
    """
    Heuristic: take the first text block (all lines up to the first blank line),
    then truncate to max_words if it’s very long.
    """
    lines = text.splitlines()
    # Collect lines until the first empty line
    block = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            break
        block.append(stripped)
    title_candidate = " ".join(block).strip()

    # If it’s too long, just take the first max_words words
    words = title_candidate.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "…"
    return title_candidate



def generate_metadata(
    path: str,
    summary_sentences: int = 3,
    keyword_count: int = 10,
    wpm: int = 200
) -> Dict[str, Any]:
    # 1. Embedded metadata
    file_meta = get_file_metadata(path)

    # 2. Raw text
    raw = extract_text(path)

    # 2.5. Language
    try:
        language = detect(raw)
    except Exception:
        language = "unknown"

    # 3. Basic info
    filename = os.path.basename(path)
    _, ext = os.path.splitext(filename)

    # 4. Title
    title = _detect_title(raw)

    # 5. NLP analysis
    keywords = extract_keywords(raw, top_n=keyword_count)
    summary = extract_summary(raw, num_sentences=summary_sentences)
    entities = extract_entities(raw)
    sections = extract_sections(raw)    # ← NEW

    # 6. Word count & reading time
    word_count = len(raw.split())
    reading_time_min = round(word_count / wpm, 2)

    # 7. Assemble
    meta: Dict[str, Any] = {
        "filename": filename,
        "filetype": ext.lower(),
        "title": title,
        "word_count": word_count,
        "reading_time_min": reading_time_min,
        "keywords": keywords,
        "summary": summary,
        "entities": [list(e) for e in entities],
        "sections": sections,            # ← NEW
        "author": file_meta.get("author", ""),
        "created_at": file_meta.get("created_at", ""),
        "language": language,
    }
    return meta


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python metadata_generator.py <path_to_file>")
        sys.exit(1)
    result = generate_metadata(sys.argv[1])
    print(json.dumps(result, indent=2))
