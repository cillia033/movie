import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
import plotly.express as px

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제의 박스오피스")

# 한국 시간(KST) 기준으로 "어제" 계산
KST = timezone(timedelta(hours=9))
yesterday = datetime.now(KST) - timedelta(days=1)
target_dt = yesterday.strftime("%Y%m%d")
target_dt_display = yesterday.strftime("%Y-%m-%d")

st.caption(f"조회 기준일: {target_dt_display}")

# Streamlit Secrets에서 인증키 읽기
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error(
        "KOBIS 인증키를 찾을 수 없습니다.\n\n"
        "Streamlit Cloud의 Secrets에 KOBIS_KEY가 등록되어 있는지 확인하세요."
    )
    st.stop()


@st.cache_data(ttl=3600)
def load_boxoffice(api_key, target_dt):
    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    params = {
        "key": api_key,
        "targetDt": target_dt
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    return response.json()


try:
    data = load_boxoffice(api_key, target_dt)

except Exception as e:
    st.error(
        "KOBIS 서버에 연결하지 못했습니다.\n\n"
        "확인 사항\n"
        "- 인터넷 연결 상태\n"
        "- KOBIS 서버 점검 여부\n"
        "- 잠시 후 다시 시도"
    )
    st.stop()

# 인증키 오류 등은 상태코드가 200이어도 faultInfo로 전달됨
if "faultInfo" in data:

    fault = data["faultInfo"]

    st.error(
        "KOBIS API 오류가 발생했습니다."
    )

    st.write("확인 사항")
    st.write("- KOBIS 인증키가 올바른지 확인")
    st.write("- Secrets의 KOBIS_KEY 값 확인")
    st.write("- API 사용 신청 상태 확인")

    st.json(fault)

    st.stop()

try:
    movies = data["boxOfficeResult"]["dailyBoxOfficeList"]

except Exception:

    st.error("응답 형식을 읽을 수 없습니다.")

    st.write("확인 사항")
    st.write("- KOBIS API 응답 구조 변경 여부")
    st.write("- 인증키 상태")
    st.write("- 조회 날짜")

    st.stop()

if len(movies) == 0:

    st.warning(
        "박스오피스 데이터가 비어 있습니다."
    )

    st.write("확인 사항")
    st.write("- 조회 날짜")
    st.write("- KOBIS 서버 상태")
    st.write("- API 응답 내용")

    st.stop()

# 표용 데이터프레임 생성
df = pd.DataFrame(movies)

# 숫자형 변환
numeric_cols = [
    "rank",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 1위 영화
top_movie = df.iloc[0]

st.subheader("🏆 박스오피스 1위")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "영화명",
        top_movie["movieNm"]
    )

with c2:
    st.metric(
        "어제 관객수",
        f"{int(top_movie['audiCnt']):,}명"
    )

with c3:
    st.metric(
        "누적 관객수",
        f"{int(top_movie['audiAcc']):,}명"
    )

st.markdown("---")

# 관객수 상위 5편 그래프
st.subheader("📊 관객수 상위 5편")

top5 = df.nlargest(5, "audiCnt")

fig = px.bar(
    top5,
    x="movieNm",
    y="audiCnt",
    text="audiCnt"
)

fig.update_traces(
    texttemplate="%{y:,}",
    textposition="outside"
)

fig.update_layout(
    xaxis_title="영화",
    yaxis_title="관객수",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# 표 표시
st.subheader("🎟️ 전체 박스오피스")

table_df = df[
    [
        "rank",
        "movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt"
    ]
].copy()

table_df.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수"
]

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)
