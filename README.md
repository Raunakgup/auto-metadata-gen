# Automated Metadata Generation System

## Overview

This project implements a scalable, automated metadata generation pipeline for unstructured documents (PDF, DOCX, TXT). It extracts rich, semantic metadata—such as titles, keywords, summaries, named entities, sections, language, word counts, reading times, and embedded author/creation-date info—and presents it through a Streamlit web interface. A complementary Jupyter notebook demonstrates the pipeline flow, and a Dockerfile simplifies deployment.

---

## Features

* **Multi-format Text Extraction**: Reliable extraction from plain text, Word (.docx), and PDF, with OCR fallback for scanned PDFs (via `pdf2image` + `pytesseract`).
* **Embedded Metadata**: Author and creation-date retrieval from DOCX core properties and PDF metadata.
* **Language Detection**: Automatic language identification using `langdetect`.
* **Title Heuristic**: Infers a document title from the first non-empty text block, truncating at 20 words with ellipsis.
* **Keyword Extraction**: Unigram TF-IDF (`scikit-learn`) for top‑N keyword identification.
* **Extractive Summarization**: Sentence-level TF-IDF scoring to select the most representative sentences.
* **Named-Entity Recognition**: `spaCy` pipeline (`en_core_web_sm`) to detect entities (PERSON, ORG, etc.).
* **Section Detection**: Heuristic rules for headings in ALL CAPS or numbered formats.
* **Web Interface**: Streamlit-based front-end (`app.py`) for file upload, metadata display, and JSON download.
* **Testing**: `pytest` tests for text extraction and metadata generation to ensure robustness.
* **Deployment**: Dockerfile for containerized deployment on port 8501.

---

## Repository Structure

```
.
├── .dockerignore           # Files and folders to exclude from Docker build context
├── pytest.ini              # Configuration for pytest
├── app.py                  # Streamlit web-app entrypoint
├── data_utils.py           # Text and embedded-file metadata extraction
├── metadata_generator.py   # Orchestrates end-to-end metadata assembly
├── nlp_utils.py            # NLP functions: keywords, summary, entities, sections
├── requirements.txt        # Python dependencies
├── Dockerfile             # Containerization for production deployment
├── samples/               # Example documents for testing and demo
│   ├── example.txt
│   ├── example.docx
│   └── example.pdf
├── example_metadata.json  # Sample output metadata for `example.pdf` in samples
├── notebooks/             # Jupyter notebook demonstrating pipeline (Do check it out to understand the flow)
│   └── metadata_pipeline.ipynb
├── tests/                 # Automated test suite
│   ├── test_data_utils.py         # Tests for text extraction
│   └── test_metadata_generator.py # Tests for metadata output structure
├── website_images/        # Images of the project website 
└── README.md              # This documentation
```

---
The website is deployed live on render, this is the link -> https://auto-metadata-gen.onrender.com/ 
Do not upload files greater then 1 MB, it will very likely crash due to the RAM and CPU limitations.

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url> && cd <repo-name>
   ```

2. **(Optional) Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download spaCy model** (if not using Docker)

   ```bash
   python -m spacy download en_core_web_sm
   ```

---

## Usage

### Streamlit Web App

Run locally:

```bash
streamlit run app.py --server.port=8501
```

* Upload a document (`.pdf`, `.docx`, `.txt`).
* View detected **Document Info**, **Title**, **Keywords**, **Summary**, **Sections**, **Entities**, and full JSON.
* Download metadata as a JSON file.

### Jupyter Notebook Demo

Open and run:

```bash
jupyter notebook notebooks/metadata_pipeline.ipynb
```

Follow step-by-step examples extracting text, generating metadata, and visualizing results.

### Command-Line Interface

For ad-hoc metadata dumps:

```bash
python metadata_generator.py path/to/document.pdf
```

Prints JSON to stdout.

---

## Algorithms & Methods

### Text Extraction (`data_utils.py`)

* **Plain Text**: Reads `.txt` files with UTF-8, ignoring errors.
* **DOCX**: Uses `python-docx` to concatenate paragraph texts.
* **PDF**: Attempts `PyPDF2` extraction; if <100 characters, uses `pdf2image` at 300 DPI plus `pytesseract` OCR.
* **Metadata**: Extracts `author` and `created_at` from PDF’s `/Author` & `/CreationDate` or DOCX core properties, formatting dates to ISO.

### Title Detection (`metadata_generator.py`)

* Gathers lines until first blank line; concatenates and truncates at 20 words, appending “…” if needed.

### NLP Processing (`nlp_utils.py`)

* **Cleaning**: Normalizes whitespace via regex.
* **Keywords**: Unigram TF-IDF restricted by `max_features` to select top tokens.
* **Summary**: Splits text into sentences (spaCy), computes TF-IDF per sentence, sums scores, selects top‑scoring sentences, and reorders them.
* **Entities**: Runs spaCy NER to extract `(text, label)` pairs.
* **Sections**: Finds headings by ALL CAPS or numbered patterns, title-cases ALL CAPS, deduplicates while preserving order.

### Performance Optimizations

* **Model Caching**: `@streamlit.cache_resource` caches spaCy model load.
* **Lazy Imports**: Defers heavy imports (e.g., `spacy` inside `load_nlp`).

---

## Testing

Run all tests with:

```bash
pytest --maxfail=1 --disable-warnings -q
```

* `test_data_utils.py`: Verifies non-empty text extraction for sample files.
* `test_metadata_generator.py`: Checks presence and validity of all metadata fields, including sections extraction via a temporary file.

---

## Deployment

### Docker Containerization

Build the Docker image:

```bash
# From the project root directory
docker build -t auto-metadata-generator .
```

Run the container, exposing port 8501 for the Streamlit app:

```bash
docker run -d --name metadata-gen \
  -p 8501:8501 \
  auto-metadata-generator
```

• **Streamlit Server**: The container’s entrypoint starts `app.py` using Streamlit on `--server.address=0.0.0.0` to listen externally on port `8501`.
• **Health Check**: Verify the container is running:

```bash
docker ps | grep metadata-gen
```

Access the web interface at [http://localhost:8501](http://localhost:8501).

---

## The Web App (`app.py`)

The Streamlit application (`app.py`) provides an intuitive UI for end-users:

1. **File Uploader**: Accepts PDF, DOCX, and TXT uploads via a drag-and-drop interface.
2. **Processing Workflow**:

   * Saves uploads to a temporary directory.
   * Invokes `generate_metadata()` with configurable summary length and keyword count.
   * Cleans up temp files after processing to conserve disk space.
3. **Metadata Display**:

   * **Document Info**: Filename, type, language, author, creation date, word count, reading time.
   * **Detected Title**: Heuristic-based title from the first text block.
   * **Keywords**: Rendered as styled HTML badges for quick scanning.
   * **Summary, Sections, Entities**: Organized under collapsible panels for a concise overview.
   * **Full JSON**: Human-readable code block and a download button for programmatic use.

This app can be extended with user authentication, custom theming, or hooks to document repositories (e.g., S3, SharePoint).

---

## Sample Outputs

* **Example Metadata**: The file `example_metadata.json` (in project root) illustrates the complete JSON structure generated for `example.pdf`.

---

## Contributing

Contributions are welcome — whether it’s bug reports, feature requests, or pull requests:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes with clear messages.
4. Submit a pull request describing your enhancements.

Please ensure new functionality includes corresponding tests in the `tests/` folder.

---

## License

This project is released under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

* **Streamlit**: Seamless UI for rapid prototypes.
* **spaCy & scikit-learn**: Powerful NLP and machine-learning tools.
* **PyPDF2 & pdf2image + pytesseract**: Robust text and OCR pipelines.
* Inspired by the need to automate document indexing and improve discoverability in large archives.
