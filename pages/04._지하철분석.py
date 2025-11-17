import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="지하철 이용량 분석", layout="wide")

# ----------------------------------------------------------
# 🔹 CSV 경로 설정 (pages 폴더 → 상위 폴더의 CSV)
# ----------------------------------------------------------
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "wnlgkcjf.csv")
CSV_PATH = os.path.abspath(CSV_PATH)

# ----------------------------------------------------------
# 🔹 CSV 로드 함수 (UTF-8 → EUC-KR 순차 시도)
# ----------------------------------------------------------
def load_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except:
        try:
            return pd.read_csv(path, encoding="euc-kr")
        except Exception as e:
            st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
            return None

# ----------------------------------------------------------
# 🔹 CSV 로드
# ----------------------------------------------------------
if not os.path.exists(CSV_PATH):
    st.error("❌ CSV 파일을 찾을 수 없습니다. 프로젝트 상위 폴더에 넣어주세요.")
    st.stop()

df = load_csv(CSV_PATH)
if df is None:
    st.stop()

st.success("CSV 파일이 정상적으로 로드되었습니다!")

# ----------------------------------------------------------
# 🔹 날짜 및 호선 선택
# ----------------------------------------------------------
st.sidebar.header("🔍 조건 선택")

sel_date = st.sidebar.date_input(
    "날짜 선택 (2025년 10월)",
    value=datetime(2025, 10, 1),
    min_value=datetime(2025, 10, 1),
    max_value=datetime(2025, 10, 31)
)

# date_input이 리스트일 경우 대비
if isinstance(sel_date, list):
    sel_date = sel_date[0]

# 날짜 형식 변환
sel_date_str = sel_date.strftime("%Y-%m-%d")

lines = sorted(df["호선"].unique())
sel_line = st.sidebar.selectbox("호선 선택", lines)

# ----------------------------------------------------------
# 🔹 데이터 필터링
# ----------------------------------------------------------
filtered = df[(df["날짜"] == sel_date_str) & (df["호선"] == sel_line)]

if filtered.empty:
    st.warning("해당 조건에 맞는 데이터가 없습니다.")
    st.stop()

# 승차 + 하차 합계
filtered["총승객"] = filtered["승차"] + filtered["하차"]

# 상위 10개 역
top10 = filtered.sort_values("총승객", ascending=False).head(10)

# ----------------------------------------------------------
# 🔹 그래프 색상 설정 (1등=빨강, 나머지=파랑→연한 그라데이션)
# ----------------------------------------------------------
colors = ["red"] + [
    f"rgba(0,0,255,{alpha})" for alpha in np.linspace(0.9, 0.3, 9)
]

# ----------------------------------------------------------
# 🔹 Plotly 막대그래프
# ----------------------------------------------------------
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=top10["역명"],
        y=top10["총승객"],
        marker=dict(color=colors),
        text=top10["총승객"],
        textposition="outside"
    )
)

fig.update_layout(
    title=f"🚇 {sel_date_str} | {sel_line} 승·하차 합계 상위 10개 역",
    xaxis_title="역명",
    yaxis_title="총 승객 수",
    template="plotly_white",
    height=550
)

# ----------------------------------------------------------
# 🔹 화면 출력
# ----------------------------------------------------------
st.plotly_chart(fig, use_container_width=True)
