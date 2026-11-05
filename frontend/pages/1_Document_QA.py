import requests
import streamlit as st

st.set_page_config(page_title="PDF Assistant")
st.title("PDF Document Assistant")

API = "http://127.0.0.1:8000"

uploaded = st.file_uploader("Choose a text-based PDF", type=["pdf"])

if st.button("Upload and index PDF"):
    if uploaded is None:
        st.warning("Choose a PDF first.")
    else:
        with st.spinner("Reading and indexing the PDF..."):
            try:
                response = requests.post(
                    f"{API}/documents",
                    files={
                        "file": (
                            uploaded.name,
                            uploaded.getvalue(),
                            "application/pdf",
                        )
                    },
                    timeout=600,
                )

                if response.ok:
                    result = response.json()
                    st.session_state.pdf_document_id = (
                        result["document_id"]
                    )
                    st.session_state.pdf_filename = uploaded.name
                    st.session_state.pop("pdf_result", None)
                    st.success(result["message"])
                else:
                    st.error(response.text[:500])
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")

document_id = st.session_state.get("pdf_document_id")

if document_id:
    st.caption(
        f"Questions will use: {st.session_state.pdf_filename}"
    )

    with st.form("pdf_question"):
        question = st.text_input("Ask a question about this PDF")
        submitted = st.form_submit_button("Search and answer")

    if submitted:
        if not question.strip():
            st.warning("Enter a question.")
        else:
            with st.spinner("Searching the PDF..."):
                try:
                    response = requests.post(
                        f"{API}/documents/ask",
                        json={
                            "question": question,
                            "document_id": document_id,
                        },
                        timeout=240,
                    )

                    if response.ok:
                        st.session_state.pdf_result = response.json()
                    else:
                        st.session_state.pop("pdf_result", None)
                        st.error(response.text[:500])
                except requests.RequestException as exc:
                    st.session_state.pop("pdf_result", None)
                    st.error(f"Question failed: {exc}")

    result = st.session_state.get("pdf_result")
    if result:
        st.markdown(result["answer"])

        with st.expander("Retrieved passages — check the evidence"):
            for source in result["sources"]:
                st.markdown(
                    f"**[{source['reference']}] "
                    f"{source['source']} — Page {source['page']}**"
                )
                st.write(source["text"])