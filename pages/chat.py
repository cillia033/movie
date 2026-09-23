import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="F1 AI Chat",
    page_icon="🏎️"
)

st.title("🏎️ F1 AI Chat")

# Secrets에서 Gemini API 키 읽기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.warning("GEMINI_API_KEY가 설정되어 있는지 확인해 주세요.")
    st.stop()

# OpenAI 라이브러리로 Gemini 연결
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 최초 1회만 대화 저장소 생성
if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Max Verstappen. "
                "Always answer only in pure English. "
                "Use simple words instead of difficult words. "
                "Stay in character as Max Verstappen."
            )
        }
    ]

# 기존 대화 출력
for msg in st.session_state.messages:

    # 시스템 프롬프트는 화면에 표시하지 않음
    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력창
prompt = st.chat_input("메시지를 입력하세요")

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 말풍선 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 말풍선
    with st.chat_message("assistant"):

        try:

            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.messages,
                stream=True
            )

            # 실시간 출력용 문자열
            full_response = ""

            # 빈 자리 생성
            placeholder = st.empty()

            # 스트리밍 출력
            for chunk in response:

                try:

                    delta = chunk.choices[0].delta.content

                    if delta:

                        full_response += delta

                        placeholder.markdown(full_response)

                except Exception:
                    pass

            # AI 답변 저장
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

        except Exception:

            st.warning(
                "AI 응답을 가져오지 못했습니다. API 키와 연결 상태를 확인해 주세요."
            )
