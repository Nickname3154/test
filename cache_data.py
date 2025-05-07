import streamlit as st
from openai import OpenAI

st.title("My LLM")
user_key = st.text_input("Enter your API key", key = "api_key",type = "password")

@st.cache_data(show_spinner="Generating response...", persist="disk")
def get_cached_response(api_key, model, prompt):
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    return completion.choices[0].message.content

client = OpenAI(api_key = st.session_state.api_key)

if user_key:
    st.text("API key entered successfully.")
    st.session_state.api_key_entered = True
else:
    st.text("Please enter your API key.")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4.1-mini"

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

        response = get_cached_response(
            user_key,
            st.session_state["openai_model"],
            prompt,
        )
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please enter your API key to continue.")
