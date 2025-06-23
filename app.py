# app.py

import os
import json
import streamlit as st
from metadata_generator import generate_metadata

# ---- Page config ----
st.set_page_config(page_title="Auto Metadata Generator", layout="wide")

# ---- App title ----
st.title("📄 Automated Metadata Generator")
st.write(
    """
    Upload a PDF, DOCX, or TXT document and get back rich, structured metadata:
    title, keywords, summary, sections, entities, language, estimated reading time, and more.
    """
)

# ---- File uploader ----
uploaded = st.file_uploader(
    "Choose a document", type=["pdf", "docx", "txt"], help="Supported formats: PDF, DOCX, TXT"
)

if uploaded:
    # Save the upload
    tmp_dir = "temp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, uploaded.name)
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    st.info(f"Processing **{uploaded.name}** …")

    # Generate metadata
    meta = generate_metadata(tmp_path, summary_sentences=3, keyword_count=10)

    # ---- Document Info (one per line) ----
    st.header("📑 Document Info")
    st.markdown(f"**Filename:**  {meta['filename']}")
    st.markdown(f"**File type:**  {meta['filetype']}")
    st.markdown(f"**Language:**  {meta['language']}")
    st.markdown(f"**Word count:**  {meta['word_count']}")
    st.markdown(f"**Estimated reading time:**  {meta['reading_time_min']} mins")
    if meta["author"]:
        st.markdown(f"**Author:**  {meta['author']}")
    if meta["created_at"]:
        st.markdown(f"**Created at:**  {meta['created_at']}")

    # ---- Full Title on its own line ----
    if meta["title"]:
        st.subheader("📌 Detected Title")
        # Use markdown/text to allow wrapping
        st.markdown(meta["title"])

    # ---- Keywords as contrasting badges ----
    if meta["keywords"]:
        st.subheader("🔑 Keywords")
        # Dark background, light text for contrast
        badges = "  ".join([
            f"<span style='background:#444;color:#fff;"
            f"padding:4px 8px;margin:2px;border-radius:4px;'>{kw}</span>"
            for kw in meta["keywords"]
        ])
        st.markdown(badges, unsafe_allow_html=True)

    # ---- Summary, Sections, Entities in Expanders ----
    with st.expander("🖋️ Summary", expanded=True):
        st.write(meta["summary"])

    with st.expander("📂 Sections (TOC)"):
        if meta["sections"]:
            for sec in meta["sections"]:
                st.write(f"- {sec}")
        else:
            st.write("No sections detected.")

    with st.expander("🏷️ Named Entities"):
        if meta["entities"]:
            st.table(meta["entities"])
        else:
            st.write("No entities detected.")

    # ---- Full JSON and Download ----
    st.subheader("🔍 Full Metadata (JSON)")
    st.code(json.dumps(meta, indent=2))

    st.download_button(
        label="📥 Download Metadata as JSON",
        data=json.dumps(meta, indent=2),
        file_name=f"{os.path.splitext(meta['filename'])[0]}_metadata.json",
        mime="application/json"
    )

    # Cleanup
    try:
        os.remove(tmp_path)
    except Exception:
        pass
