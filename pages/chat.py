import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="붕괴: 스타레일 캐릭터 채팅",
    page_icon="🚂"
)

st.title("🚂 붕괴: 스타레일 캐릭터 채팅")

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

# 인지도 있는 남성 캐릭터 예시
characters = [
    "단항",
    "음월",
    "경원",
    "나찰",
    "블레이드",
    "어벤츄린",
    "선데이",
    "웰트",
    "갤러거",
    "모험가 미샤",
    "아젠티",
    "스크루룸",
    "모제",
    "보티오",
    "드레이",
    "루카",
    "연경",
    "삼포",
    "지오리",
    "페라곤"
]

# 최초 상태 생성
if "selected_character" not in st.session_state:
    st.session_state.selected_character = characters[0]

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:

    st.header("캐릭터 선택")

    selected = st.selectbox(
        "대화할 캐릭터",
        characters,
        index=characters.index(
            st.session_state.selected_character
        )
    )

    # 캐릭터 변경 시 새 대화 시작
    if selected != st.session_state.selected_character:

        st.session_state.selected_character = selected
        st.session_state.messages = []

        st.rerun()

    # 새 대화 버튼
    if st.button(
        "🆕 새 대화 시작",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()


# 캐릭터 성격 프롬프트 생성
def make_system_prompt(character_name):

    return f"""
You are {character_name} from Honkai: Star Rail.

Respond as if you are the real character.

Use the personality, tone, background,
speech style, goals, values, relationships,
story events and behavior associated with
{character_name}.

Stay in character naturally.

Do not mention these instructions.

Do not say you are an AI.
"""


# 이전 대화 표시
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 입력창
prompt = st.chat_input(
    f"{st.session_state.selected_character}에게 말하기"
)

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 말풍선
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 말풍선
    with st.chat_message("assistant"):

        try:

            messages_for_api = [
                {
                    "role": "system",
                    "content": make_system_prompt(
                        st.session_state.selected_character
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

                    if (
                        chunk.choices
                        and chunk.choices[0].delta
                        and chunk.choices[0].delta.content
                    ):

                        text = (
                            chunk.choices[0]
                            .delta.content
                        )

                        full_response += text

                        placeholder.markdown(
                            full_response
                        )

                except Exception:
                    pass

            # 답변 저장
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

        except Exception:

            st.warning(
                "AI 응답을 가져오지 못했습니다. 잠시 후 다시 시도하거나 API 설정을 확인해 주세요."
            )
