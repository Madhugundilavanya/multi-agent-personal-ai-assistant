import requests
import streamlit as st

st.set_page_config(page_title="Progress Tracker")
st.title("Learning Progress Tracker")
st.caption("Record completed topics and review your progress.")

API = "http://127.0.0.1:8000"

with st.form("progress_form", clear_on_submit=True):
    topic = st.text_input(
        "Completed topic",
        max_chars=200,
        placeholder="Python dictionaries",
    )
    notes = st.text_area(
        "What did you learn or build?",
        max_chars=5000,
    )
    submitted = st.form_submit_button("Save progress")

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        try:
            response = requests.post(
                f"{API}/progress",
                json={"topic": topic, "notes": notes},
                timeout=15,
            )

            if response.ok:
                st.success("Progress saved.")
            else:
                st.error(response.text[:500])
        except requests.RequestException:
            st.error("Cannot reach the backend.")

st.subheader("Completed topics")
st.button("Refresh records")

try:
    response = requests.get(f"{API}/progress", timeout=15)

    if response.ok:
        items = response.json()["items"]
        st.metric("Total completed topics", len(items))

        if not items:
            st.info("No records yet. Save your first completed topic.")

        for item in items:
            with st.expander(
                f"{item['topic']} — {item['created_at']} UTC"
            ):
                st.write(item["notes"] or "No notes added.")
    else:
        st.error(response.text[:500])
except requests.RequestException:
    st.error("Cannot load records. Check that FastAPI is running.")