import streamlit as st
from openai import OpenAI

st.title("My LLM")
user_key = st.text_input("Enter your API key", key = "api_key")

client = OpenAI(api_key = st.session_state.key)

if user_key:
    st.text("API key entered successfully.")
    st.session_state.api_key_entered = True
else:
    st.text("Please enter your API key.")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "api_key_entered" in st.session_state and st.session_state.api_key_entered:
    if prompt := st.chat_input("Enter your question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please enter your API key to continue.")