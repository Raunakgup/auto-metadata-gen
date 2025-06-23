import pytest
from data_utils import extract_text

@pytest.mark.parametrize("fname", [
    "samples/example.txt",
    "samples/example.docx",
    "samples/example.pdf",
])
def test_extract_text_nonempty(fname):
    text = extract_text(fname)
    assert isinstance(text, str)
    assert len(text) > 0
