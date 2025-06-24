import os  
import json  
from typing import Any, Dict  # for type annotations of metadata dictionary

from data_utils import extract_text, get_file_metadata  # utilities for text and basic metadata extraction
from nlp_utils import (
    extract_keywords,  
    extract_summary,   
    extract_entities,  
    extract_sections,  
)
from langdetect import detect  # language detection library for raw text


def _detect_title(text: str, max_words: int = 20) -> str:
    """
    Heuristic title detection based on the first non-empty block of text.

    1. Split text into lines and collect lines until the first blank line.
    2. Join those lines as the title candidate.
    3. If the candidate exceeds `max_words`, truncate and append an ellipsis.

    Parameters:
        text: full document text
        max_words: maximum number of words in the detected title
    Returns:
        A string representing the inferred title (possibly truncated)
    """
    lines = text.splitlines()

    # Gather lines until an empty line signifies end of title block
    block = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            break
        block.append(stripped)

    # Combine collected lines into a single candidate
    title_candidate = " ".join(block).strip()

    # Truncate if too many words
    words = title_candidate.split()
    if len(words) > max_words:
        # Keep only the first `max_words` words, add ellipsis
        return " ".join(words[:max_words]) + "…"
    return title_candidate


def generate_metadata(
    path: str,
    summary_sentences: int = 3,
    keyword_count: int = 10,
    wpm: int = 200
) -> Dict[str, Any]:
    """
    Generate structured metadata for a given document.

    Steps:
    1. Extract embedded file metadata (author, creation date).
    2. Extract raw text content (with OCR fallback for PDFs).
    3. Detect document language.
    4. Infer a title via heuristic.
    5. Perform NLP analyses: keywords, summary, entities, sections.
    6. Compute word count and estimated reading time.
    7. Assemble all details into a metadata dictionary.

    Parameters:
        path: filepath to the document
        summary_sentences: number of sentences for summary output
        keyword_count: maximum number of keywords to extract
        wpm: words-per-minute reading speed for time estimate
    Returns:
        Dict[str, Any]: metadata including filename, type, text analytics, and file metadata
    """
    # Get embedded metadata from file (author, creation date)
    file_meta = get_file_metadata(path)

    # Extract the full raw text content from the file
    raw = extract_text(path)

    # Identify the document language; fallback to 'unknown'
    try:
        language = detect(raw)
    except Exception:
        language = "unknown"

    # Derive basic file information
    filename = os.path.basename(path)  # e.g., 'document.pdf'
    _, ext = os.path.splitext(filename)  # split to get file extension

    # Infer a title from the first text block
    title = _detect_title(raw)

    # Perform NLP-based metadata extraction
    keywords = extract_keywords(raw, top_n=keyword_count)  
    summary = extract_summary(raw, num_sentences=summary_sentences)  
    entities = extract_entities(raw) 
    sections = extract_sections(raw)  

    # 6. Compute word count and reading time
    word_count = len(raw.split()) 
    reading_time_min = round(word_count / wpm, 2)  # estimated minutes

    # 7. Consolidate all metadata into a single dict
    meta: Dict[str, Any] = {
        "filename": filename,
        "filetype": ext.lower(),
        "title": title,
        "word_count": word_count,
        "reading_time_min": reading_time_min,
        "keywords": keywords,
        "summary": summary,
        "entities": [list(e) for e in entities],  # convert tuples to lists for JSON
        "sections": sections,
        "author": file_meta.get("author", ""),
        "created_at": file_meta.get("created_at", ""),
        "language": language,
    }
    return meta


if __name__ == "__main__":
    # CLI entrypoint for ad-hoc metadata generation
    import sys
    if len(sys.argv) != 2:
        print("Usage: python metadata_generator.py <path_to_file>")
        sys.exit(1)

    result = generate_metadata(sys.argv[1])
    # Pretty-print the JSON metadata to stdout
    print(json.dumps(result, indent=2))
