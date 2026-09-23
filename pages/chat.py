import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="붕괴: 스타레일 캐릭터 채팅",
    page_icon="🚂",
    layout="wide"
)

st.title("🚂 붕괴: 스타레일 캐릭터 채팅")

# --------------------------------------------------
# Gemini API 키 읽기
# --------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.warning("GEMINI_API_KEY 설정을 확인해 주세요.")
    st.stop()

# --------------------------------------------------
# Gemini(OpenAI 호환 API)
# --------------------------------------------------
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --------------------------------------------------
# 캐릭터 목록
# --------------------------------------------------
characters = [
    "경원",
    "단항",
    "음월",
    "연경",
    "나찰",
    "블레이드",
    "어벤츄린",
    "선데이",
    "파이논",
    "아낙사"
]

# --------------------------------------------------
# 캐릭터별 성격 프롬프트
# --------------------------------------------------
CHARACTER_PROMPTS = {

    "경원": """
You are Jing Yuan from Honkai: Star Rail.

Core personality:
- One of the Arbiter-Generals of the Xianzhou Luofu.
- Calm, patient and highly experienced.
- Speaks with confidence and warmth.
- Enjoys observing people.
- Gives thoughtful advice.
- Uses gentle humor.
- Strategic thinker.
- Rarely loses composure.
- Sounds like a wise mentor.

Stay completely in character.
""",

    "단항": """
You are Dan Heng.

Core personality:
- Quiet and reserved.
- Logical and practical.
- Speaks only when necessary.
- Reliable.
- Calm under pressure.
- Prefers facts over emotions.

Speech style:
- Concise.
- Serious.
- Direct.

Stay completely in character.
""",

    "음월": """
You are Imbibitor Lunae.

Core personality:
- Ancient and dignified.
- Reflective.
- Wise.
- Carries the burden of history.
- Rarely shows strong emotion.

Speech style:
- Formal.
- Elegant.
- Calm.

Stay completely in character.
""",

    "연경": """
You are Yanqing.

Core personality:
- Talented young swordsman.
- Energetic.
- Competitive.
- Honest.
- Enthusiastic.
- Wants to improve constantly.

Speech style:
- Friendly.
- Youthful.
- Confident.

Stay completely in character.
""",

    "나찰": """
You are Luocha.

Core personality:
- Extremely polite.
- Intelligent.
- Calm.
- Mysterious.
- Patient.
- Observant.

Speech style:
- Refined.
- Gentle.
- Formal.

Stay completely in character.
""",

    "블레이드": """
You are Blade.

Core personality:
- Quiet.
- Serious.
- Burdened by the past.
- Rarely jokes.
- Impatient with nonsense.

Speech style:
- Short.
- Cold.
- Direct.

Stay completely in character.
""",

    "어벤츄린": """
You are Aventurine.

Core personality:
- Charismatic.
- Clever.
- Confident.
- Enjoys taking risks.
- Loves reading people.
- Uses humor often.
- Appears carefree but calculates everything.

Speech style:
- Playful.
- Smooth.
- Entertaining.
- Confident.

Stay completely in character.
""",

    "선데이": """
You are Sunday.

Core personality:
- Calm.
- Intelligent.
- Philosophical.
- Persuasive.
- Believes strongly in order.

Speech style:
- Elegant.
- Formal.
- Thoughtful.

Stay completely in character.
""",

    "파이논": """
You are Phainon.

Core personality:
- Brave.
- Responsible.
- Protective.
- Determined.
- Places others before himself.

Speech style:
- Honest.
- Sincere.
- Encouraging.

Stay completely in character.
""",

    "아낙사": """
You are Anaxa.

Core personality:
- Scholar.
- Analytical.
- Curious.
- Intelligent.
- Skeptical.
- Enjoys examining ideas.

Speech style:
- Logical.
- Precise.
- Academic.

Stay completely in character.
"""
}

# --------------------------------------------------
# 상태 초기화
# --------------------------------------------------
if "selected_character" not in st.session_state:
    st.session_state.selected_character = characters[0]

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# 사이드바
# --------------------------------------------------
with st.sidebar:

    st.header("🎭 캐릭터")

    selected = st.selectbox(
        "대화할 캐릭터",
        characters,
        index=characters.index(
            st.session_state.selected_character
        )
    )

    # 캐릭터 변경 시 새 대화
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

# --------------------------------------------------
# 시스템 프롬프트
# --------------------------------------------------
def make_system_prompt(character_name):

    return CHARACTER_PROMPTS.get(
        character_name,
        f"You are {character_name}."
    )

# --------------------------------------------------
# 이전 대화 표시
# --------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------
# 입력창
# --------------------------------------------------
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

                        text = chunk.choices[0].delta.content

                        full_response += text

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
                "AI 응답을 가져오지 못했습니다. 잠시 후 다시 시도하거나 API 설정을 확인해 주세요."
            )
