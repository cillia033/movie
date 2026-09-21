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

# 한국 시간 기준 어제 날짜 계산
KST = timezone(timedelta(hours=9))
yesterday = datetime.now(KST) - timedelta(days=1)

target_dt = yesterday.strftime("%Y%m%d")
target_dt_display = yesterday.strftime("%Y-%m-%d")

st.caption(f"조회 기준일: {target_dt_display}")

# Secrets에서 KOBIS 인증키 읽기
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error(
        "KOBIS 인증키를 찾을 수 없습니다.\n\n"
        "Streamlit Cloud Secrets에 KOBIS_KEY를 등록했는지 확인하세요."
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


@st.cache_data(ttl=86400)
def get_movie_info(api_key, movie_cd):

    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "movie/searchMovieInfo.json"
    )

    params = {
        "key": api_key,
        "movieCd": movie_cd
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        return data["movieInfoResult"]["movieInfo"]

    except Exception:
        return None


# 박스오피스 조회
try:
    data = load_boxoffice(
        api_key,
        target_dt
    )

except Exception:

    st.error(
        "KOBIS 서버 연결에 실패했습니다.\n\n"
        "잠시 후 다시 시도하세요."
    )

    st.stop()


# 인증키 오류
if "faultInfo" in data:

    st.error("KOBIS API 오류")

    st.write("확인 사항")
    st.write("- KOBIS_KEY 값")
    st.write("- API 사용 승인 여부")
    st.write("- 일일 호출 제한")

    st.json(data["faultInfo"])

    st.stop()


# 영화 목록 읽기
try:

    movies = data["boxOfficeResult"]["dailyBoxOfficeList"]

except Exception:

    st.error("API 응답 구조를 읽을 수 없습니다.")
    st.stop()


if len(movies) == 0:

    st.warning(
        "박스오피스 데이터가 비어 있습니다."
    )

    st.stop()


# 데이터프레임 생성
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

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# 애니메이션 영화만 추출
animation_rows = []

if "movieCd" in df.columns:

    with st.spinner("애니메이션 영화 정보를 확인하는 중입니다..."):

        for _, row in df.iterrows():

            movie_info = get_movie_info(
                api_key,
                row["movieCd"]
            )

            if movie_info is None:
                continue

            genres = [
                g["genreNm"]
                for g in movie_info.get("genres", [])
            ]

            if "애니메이션" in genres:

                animation_rows.append(
                    {
                        "순위": int(row["rank"]),
                        "영화명": row["movieNm"],
                        "개봉일": row["openDt"],
                        "관객수": int(row["audiCnt"]),
                        "누적관객": int(row["audiAcc"]),
                        "스크린수": int(row["scrnCnt"])
                    }
                )

animation_df = pd.DataFrame(animation_rows)

if not animation_df.empty:

    animation_df = animation_df.sort_values(
        "순위"
    )


# 1위 영화 카드
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

top5 = df.nlargest(
    5,
    "audiCnt"
)

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


# 표 영역
left, right = st.columns([2, 1])

with left:

    st.subheader("🎬 전체 박스오피스")

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

with right:

    st.subheader("🎞️ 애니메이션 순위")

    if animation_df.empty:

        st.info(
            "어제 박스오피스 TOP10에 "
            "애니메이션 영화가 없습니다."
        )

    else:

        st.dataframe(
            animation_df,
            use_container_width=True,
            hide_index=True
        )
