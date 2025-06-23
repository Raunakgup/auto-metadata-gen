# tests/test_metadata_generator.py

import pytest
from metadata_generator import generate_metadata

SAMPLES = [
    ("samples/example.txt", ".txt"),
    ("samples/example.pdf", ".pdf"),
    ("samples/example.docx", ".docx"),  
]

@pytest.mark.parametrize("path, ext", SAMPLES)
def test_generate_metadata_contains_all_fields(path, ext):
    meta = generate_metadata(path, summary_sentences=1, keyword_count=5)

    # Basic fields
    assert meta["filename"].endswith(ext)
    assert meta["filetype"] == ext
    assert isinstance(meta["title"], str)

    # NLP fields
    assert isinstance(meta["keywords"], list)
    assert 0 < len(meta["keywords"]) <= 5
    assert isinstance(meta["summary"], str) and len(meta["summary"]) > 0
    assert isinstance(meta["entities"], list)

    # File metadata fields
    assert "author" in meta and isinstance(meta["author"], str)
    assert "created_at" in meta and isinstance(meta["created_at"], str)

    # Language
    assert "language" in meta and isinstance(meta["language"], str) and len(meta["language"]) > 0

    # New: reading time
    assert "reading_time_min" in meta
    assert isinstance(meta["reading_time_min"], float)
    # reading_time_min should be > 0 and roughly word_count / 200
    assert meta["reading_time_min"] > 0
    assert abs(meta["reading_time_min"] - meta["word_count"]/200) < 0.1

    # Word count sanity
    assert isinstance(meta["word_count"], int) and meta["word_count"] > 0

def test_sections_field_present(tmp_path):
    # Create a dummy text file with headings
    content = "\n".join([
        "INTRODUCTION",
        "1. First Section",
        "Some paragraph.",
        "CONCLUSION"
    ])
    p = tmp_path / "test.txt"
    p.write_text(content, encoding="utf-8")

    meta = generate_metadata(str(p), summary_sentences=1, keyword_count=2)
    # Sections should pick up exactly the three headings
    assert "sections" in meta
    assert meta["sections"] == ["Introduction", "1. First Section", "Conclusion"]
