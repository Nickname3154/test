import streamlit as st
from openai import OpenAI

st.title("My LLM")
user_key = st.text_input("Enter your API key")
user_Q = st.text_input("write your question")

client = OpenAI(api_key = user_key)
