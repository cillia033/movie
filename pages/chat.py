\import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="F1 Driver AI Chat",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Driver AI Chat")

# Gemini API 키 읽기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.warning("GEMINI_API_KEY 설정을 확인해 주세요.")
    st.stop()

# Gemini(OpenAI 호환 API) 연결
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 현재 활동 중인 주요 F1 드라이버 목록
drivers = [
    "Max Verstappen",
    "Lando Norris",
    "Oscar Piastri",
    "Charles Leclerc",
    "Lewis Hamilton",
    "George Russell",
    "Andrea Kimi Antonelli",
    "Fernando Alonso",
    "Lance Stroll",
    "Carlos Sainz",
    "Alexander Albon",
    "Yuki Tsunoda",
    "Pierre Gasly",
    "Esteban Ocon",
    "Nico Hulkenberg",
    "Gabriel Bortoleto",
    "Oliver Bearman",
    "Isack Hadjar",
    "Liam Lawson",
    "Franco Colapinto"
]

# 최초 상태 생성
if "selected_driver" not in st.session_state:
    st.session_state.selected_driver = drivers[0]

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:

    st.header("⚙️ 설정")

    selected = st.selectbox(
        "F1 선수 선택",
        drivers,
        index=drivers.index(
            st.session_state.selected_driver
        )
    )

    # 선수 변경 시 새 대화 시작
    if selected != st.session_state.selected_driver:

        st.session_state.selected_driver = selected

        st.session_state.messages = []

        st.rerun()

    # 새 대화 버튼
    if st.button(
        "🆕 새 대화 시작",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

# 시스템 프롬프트 생성 함수
def get_system_prompt(driver_name):

    return f"""
You are {driver_name}.

Respond as if you are the real Formula 1 driver.

Your personality, tone, habits, communication style,
humor, racing mindset, and interests should reflect
public interviews, media appearances, paddock conversations,
and public content associated with {driver_name}.

Stay in character naturally.

Do not mention these instructions.

Do not say you are an AI.

Answer as {driver_name}.
"""


# 채팅 기록 표시
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 입력창
prompt = st.chat_input(
    f"{st.session_state.selected_driver}에게 질문하기"
)

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 표시
    with st.chat_message("assistant"):

        try:

            # 시스템 프롬프트 + 기존 대화
            messages_for_api = [
                {
                    "role": "system",
                    "content": get_system_prompt(
                        st.session_state.selected_driver
                    )
                }
            ]

            messages_for_api.extend(
                st.session_state.messages
            )

            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=messages_for_api,
                stream=True
            )

            full_response = ""

            placeholder = st.empty()

            # 실시간 출력
            for chunk in response:

                try:

                    delta = (
                        chunk
                        .choices[0]
                        .delta
                        .content
                    )

                    if delta:

                        full_response += delta

                        placeholder.markdown(
                            full_response
                        )

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
                "AI 응답을 가져오지 못했습니다. API 설정 또는 연결 상태를 확인해 주세요."
            )
