# nlp_utils.py

from typing import List, Tuple
import re
import streamlit
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

@streamlit.cache_resource
def load_nlp():
    import spacy
    return spacy.load("en_core_web_sm")

nlp = load_nlp()

def clean_text(text: str) -> str:
    """Basic cleanup: normalize whitespace."""
    return re.sub(r"\s+", " ", text).strip()

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Top‑N keywords via unigram TF‑IDF."""
    cleaned = clean_text(text)
    vect = TfidfVectorizer(stop_words="english", max_features=top_n)
    tfidf = vect.fit_transform([cleaned])
    return vect.get_feature_names_out().tolist()


def extract_summary(text: str, num_sentences: int = 3) -> str:
    """Extractive summary by TF‑IDF scoring of sentences."""
    cleaned = clean_text(text)
    doc = nlp(cleaned)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    if not sentences:
        return ""

    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    vect = TfidfVectorizer(stop_words="english")
    tf = vect.fit_transform(sentences)
    scores = tf.sum(axis=1).A1
    top_idxs = scores.argsort()[-num_sentences:][::-1]
    ordered = sorted(top_idxs)
    return " ".join(sentences[i] for i in ordered)


def extract_entities(text: str) -> List[Tuple[str, str]]:
    """Named‑entity recognition via spaCy."""
    doc = nlp(clean_text(text))
    return [(ent.text, ent.label_) for ent in doc.ents]


def extract_sections(text: str) -> List[str]:
    """
    Simple heuristic to extract section headings:
    - Lines in ALL CAPS (length between 3 and 60 chars)
    - Or lines that start with a digit and a dot (e.g. '1. Introduction')
    """
    sections = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 60:
            continue
        # ALL CAPS heuristic
        if re.match(r'^[A-Z0-9 \-]+$', stripped) and any(c.isalpha() for c in stripped):
            sections.append(stripped.title())
        # Numbered headings
        elif re.match(r'^\d+\. ?[A-Za-z].*', stripped):
            # e.g. "1. Introduction"
            sections.append(stripped)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for sec in sections:
        if sec not in seen:
            seen.add(sec)
            unique.append(sec)
    return unique
