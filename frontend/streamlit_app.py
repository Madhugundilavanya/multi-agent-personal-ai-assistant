import requests
import streamlit as st

st.set_page_config(page_title="Personal AI Assistant")
st.title("Multi-Agent Personal AI Assistant")

agents = {
    "Auto": "auto",
    "Learning Coach": "learning",
    "Interview Coach": "interview",
    "Goal Planner": "planner",
}
selected = st.selectbox("Choose an assistant", list(agents))
agent = agents[selected]

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

messages = st.session_state.conversations.setdefault(agent, [])

if st.button("Clear this conversation"):
    messages.clear()
    st.rerun()

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Type your message"):
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "message": question,
                        "agent": agent,
                        "history": messages[-20:],
                    },
                    timeout=200,
                )

                if response.ok:
                    result = response.json()
                    answer = result["answer"]
                    st.caption(f"Handled by: {result['agent'].title()}")
                    st.markdown(answer)
                    messages.extend([
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ])
                else:
                    st.error(
                        f"Request failed ({response.status_code}): "
                        f"{response.text[:500]}"
                    )
            except requests.RequestException:
                st.error(
                    "Cannot reach the backend. "
                    "Check that FastAPI is running."
                )