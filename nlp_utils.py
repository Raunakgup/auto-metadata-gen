from typing import List, Tuple  # for type annotations
import re 
import streamlit  
import spacy  # for NLP processing
from sklearn.feature_extraction.text import TfidfVectorizer  # for keyword and summary extraction


@streamlit.cache_resource
def load_nlp():
    """
    Lazily load and cache the spaCy language model to avoid repeated loads.

    Returns:
        A spaCy Language object for processing English text.
    """

    import spacy
    return spacy.load("en_core_web_sm")


nlp = load_nlp()


def clean_text(text: str) -> str:
    """
    Normalize whitespace in text.

    Replaces any sequence of whitespace characters (spaces, newlines, tabs)
    with a single space, and trims leading/trailing spaces.

    Parameters:
        text: raw document text
    Returns:
        Cleaned text with uniform spacing.
    """
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Identify the top N keywords using unigram TF-IDF.

    Steps:
    1. Clean text (whitespace normalization).
    2. Vectorize text into TF-IDF features, limited to top_n features.
    3. Return the feature names (keywords).

    Parameters:
        text: input document text
        top_n: number of keywords to extract
    Returns:
        List of keyword strings
    """
    cleaned = clean_text(text)
    vect = TfidfVectorizer(stop_words="english", max_features=top_n)
    tfidf = vect.fit_transform([cleaned])  # single-document TF-IDF
    return vect.get_feature_names_out().tolist()


def extract_summary(text: str, num_sentences: int = 3) -> str:
    """
    Generate an extractive summary by scoring and selecting sentences.

    Approach:
    1. Clean text and split into sentences via spaCy pipeline.
    2. If total sentences ≤ num_sentences, return the full text.
    3. Otherwise, apply TF-IDF to sentence-level corpus.
    4. Score each sentence by summing its TF-IDF values.
    5. Select the top num_sentences sentences and reconstruct summary
       in their original order.

    Parameters:
        text: document text to summarize
        num_sentences: number of sentences to include
    Returns:
        Concatenated sentences as the summary string.
    """
    cleaned = clean_text(text)
    doc = nlp(cleaned)  # process text for sentence segmentation
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # Return early if not enough sentences
    if not sentences:
        return ""
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    # Compute sentence-level TF-IDF
    vect = TfidfVectorizer(stop_words="english")
    tf = vect.fit_transform(sentences)
    scores = tf.sum(axis=1).A1  # sum TF-IDF scores per sentence

    # Identify top sentence indices
    top_idxs = scores.argsort()[-num_sentences:][::-1]
    # Sort indices to preserve original order in summary
    ordered = sorted(top_idxs)
    return " ".join(sentences[i] for i in ordered)


def extract_entities(text: str) -> List[Tuple[str, str]]:
    """
    Perform named-entity recognition using spaCy.

    Parameters:
        text: document text for NER
    Returns:
        A list of tuples (entity_text, entity_label) for each detected entity.
    """
    doc = nlp(clean_text(text))  
    return [(ent.text, ent.label_) for ent in doc.ents]


def extract_sections(text: str) -> List[str]:
    """
    Heuristic extraction of section headings from text based on formatting patterns.

    Patterns detected:
    - Lines in all uppercase (3 to 60 chars) that contain letters.
    - Numbered headings starting with digits and a dot (e.g., '1. Introduction').

    Returns unique headings preserving original document order.

    Parameters:
        text: full document text
    Returns:
        List of detected section heading strings.
    """
    sections = []
    for line in text.splitlines():
        stripped = line.strip()
        # Skip blanks and overly long lines
        if not stripped or len(stripped) > 60:
            continue

        if re.match(r'^[A-Z0-9 \-]+$', stripped) and any(c.isalpha() for c in stripped):
            sections.append(stripped.title())
       
        elif re.match(r'^\d+\. ?[A-Za-z].*', stripped):
            sections.append(stripped)
    
    seen = set()
    unique = []
    for sec in sections:
        if sec not in seen:
            seen.add(sec)
            unique.append(sec)
    return unique
