import streamlit as st
from openai import OpenAI
import tempfile
import time

st.title("📄 ChatPDF")

api_key = st.text_input("Enter your OpenAI API Key", type="password")
client = OpenAI(api_key=api_key) if api_key else None

if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file and api_key and client:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    with st.spinner("PDF를 업로드하고 벡터화하는 중입니다..."):
        file = client.files.create(file=open(tmp_file_path, "rb"), purpose="assistants")

        vector_store = client.beta.vector_stores.create(name="ChatPDF Vector Store")
        st.session_state.vector_store_id = vector_store.id

        client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[file.id],
        )

        assistant = client.beta.assistants.create(
            name="ChatPDF Assistant",
            instructions="업로드된 PDF 파일 내용을 바탕으로 질문에 답하세요.",
            model="gpt-4.1-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        st.session_state.assistant_id = assistant.id

        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    st.success("PDF 업로드 및 설정 완료! 질문을 입력해보세요.")

if st.button("❌ Clear"):
    if st.session_state.vector_store_id:
        client.beta.vector_stores.delete(st.session_state.vector_store_id)
    st.session_state.vector_store_id = None
    st.session_state.assistant_id = None
    st.session_state.thread_id = None
    st.success("벡터 스토어 및 세션이 초기화되었습니다.")

if st.session_state.assistant_id and st.session_state.thread_id:
    if prompt := st.chat_input("PDF에 대해 질문하세요"):
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        with st.spinner("답변 생성 중..."):
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(1)

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            answer = messages.data[0].content[0].text.value

        with st.chat_message("assistant"):
            st.markdown(answer)

