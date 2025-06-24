import os  
import json  # for serializing metadata to JSON format
import streamlit as st  # for building the web interface
from metadata_generator import generate_metadata  

# Configure the Streamlit app's basic properties
st.set_page_config(
    page_title="Auto Metadata Generator",  # title of the browser tab
    layout="wide"  
)

# Display the main title and introductory text on the page
st.title("📄 Automated Metadata Generator")
st.write(
    """
    Upload a PDF, DOCX, or TXT document and get back rich, structured metadata:
    title, keywords, summary, sections, entities, language, estimated reading time, and more.
    """
)

# Allow users to upload a document file (PDF, DOCX, or TXT)
uploaded = st.file_uploader(
    "Choose a document", 
    type=["pdf", "docx", "txt"],  # Restrict to supported file extensions
    help="Supported formats: PDF, DOCX, TXT"  
)

# process it
if uploaded:
    # Create a temporary directory (if it doesn't exist) to store the uploaded file
    tmp_dir = "temp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)

    # Build the full path for saving the uploaded file locally
    tmp_path = os.path.join(tmp_dir, uploaded.name)

    # Write the uploaded file's bytes to disk for downstream processing
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    # Processing has started
    st.info(f"Processing **{uploaded.name}** …")

    # Call the metadata generation routine
    # summary_sentences: number of sentences in the generated summary (modifiable)
    # keyword_count: maximum number of keywords to extract (also adjustable)
    meta = generate_metadata(
        tmp_path,
        summary_sentences=3,
        keyword_count=10
    )

    # Display basic document information
    st.header("📑 Document Info")

    # Show filename, detected file type, language, word count, and reading time
    st.markdown(f"**Filename:**  {meta['filename']}")
    st.markdown(f"**File type:**  {meta['filetype']}")
    st.markdown(f"**Language:**  {meta['language']}")
    st.markdown(f"**Word count:**  {meta['word_count']}")
    st.markdown(f"**Estimated reading time:**  {meta['reading_time_min']} mins")

    # Display author and creation date if available
    if meta.get("author"):
        st.markdown(f"**Author:**  {meta['author']}")
    if meta.get("created_at"):
        st.markdown(f"**Created at:**  {meta['created_at']}")

    # Display the detected document title 
    if meta.get("title"):
        st.subheader("📌 Detected Title")
        # Using markdown allows the title text to wrap nicely
        st.markdown(meta["title"])

    # Present extracted keywords as visual badges 
    if meta.get("keywords"):
        st.subheader("🔑 Keywords")
        # Build HTML snippets for each keyword badge 
        badges = "  ".join([
            (
                f"<span style='background:#444;color:#fff;"
                f"padding:4px 8px;margin:2px;border-radius:4px;'>{kw}</span>"
            )
            for kw in meta["keywords"]
        ])
        # Render in the Streamlit app
        st.markdown(badges, unsafe_allow_html=True)

    # Expandable section for the document summary 
    with st.expander("🖋️ Summary", expanded=True):
        st.write(meta["summary"])

    # Expandable table of contents (sections) 
    with st.expander("📂 Sections (TOC)"):
        sections = meta.get("sections", [])
        if sections:
            # List each section heading
            for sec in sections:
                st.write(f"- {sec}")
        else:
            st.write("No sections detected.")

    # Expandable list of named entities 
    with st.expander("🏷️ Named Entities"):
        entities = meta.get("entities")
        if entities:
            # Display entities in a table (pandas DataFrame expected)
            st.table(entities)
        else:
            st.write("No entities detected.")

    # Show the full metadata JSON for advanced users
    st.subheader("🔍 Full Metadata (JSON)")
    st.code(json.dumps(meta, indent=2))

    # Provide a download button so users can save the metadata locally
    st.download_button(
        label="📥 Download Metadata as JSON",
        data=json.dumps(meta, indent=2),
        file_name=f"{os.path.splitext(meta['filename'])[0]}_metadata.json",
        mime="application/json"
    )

    # Cleanup temporary file 
    try:
        os.remove(tmp_path)  # delete the file after processing to save disk space
    except Exception:
        # If cleanup fails, proceed silently (no user-facing error)
        pass
