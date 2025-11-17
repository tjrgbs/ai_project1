import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import os

st.set_page_config(page_title="지하철 상위역 분석", layout="wide")

st.title("🚇 2025년 10월 — 호선별 승하차 상위 10개 역 분석")

# -----------------------------------------------------------
# 🔹 파일 읽기 (UTF-8 → EUC-KR 순차 시도)
# -----------------------------------------------------------
def load_csv(file):
    try:
        return pd.read_csv(file, encoding="utf-8")
    except:
        try:
            return pd.read_csv(file, encoding="euc-kr")
        except Exception as e:
            st.error(f"CSV 파일을 읽는 중 오류 발생: {e}")
            return None

# -----------------------------------------------------------
# 🔹 컬럼 자동 감지
# -----------------------------------------------------------
def guess_columns(df):
    cols = [c.lower() for c in df.columns]

    def find(*names):
        for name in names:
            for c in df.columns:
                if name in c.lower():
                    return c
        return None

    return {
        "date": find("사용일자", "일자", "date", "날짜"),
        "line": find("호선", "line"),
        "station": find("역명", "역", "station"),
        "boarding": find("승차", "boarding"),
        "alighting": find("하차", "alighting")
    }

# -----------------------------------------------------------
# 🔹 색상 생성 (1등 빨강, 나머지 파랑 그라데이션)
# -----------------------------------------------------------
def make_color_list(n):
    colors = []
    colors.append("rgba(230,40,40,1)")  # 1등 빨강

    start = np.array([30, 70, 200])
    end = np.array([180, 200, 255])

    for i in range(1, n):
        t = (i - 1) / max(1, n - 2)
        rgb = (1 - t) * start + t * end
        r, g, b = rgb.astype(int)
        colors.append(f"rgba({r},{g},{b},0.9)")
    return colors

# -----------------------------------------------------------
# 🔹 파일 업로드 또는 기본 파일 로드
# -----------------------------------------------------------
uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])

df = None
default_path = "/mnt/data/wnlgkcjf.csv"

if uploaded:
    df = load_csv(uploaded)
elif os.path.exists(default_path):
    st.info(f"기본 데이터 파일을 사용합니다: {default_path}")
    df = load_csv(default_path)
else:
    st.warning("CSV 파일을 업로드해 주세요.")

# -----------------------------------------------------------
# 🔹 본격 분석
# -----------------------------------------------------------
if df is not None:
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    cols = guess_columns(df)
    st.write("자동 감지된 컬럼:", cols)

    # 날짜 변환
    if cols["date"]:
        df[cols["date"]] = pd.to_datetime(df[cols["date"]], errors="coerce")

    # -------------------------------------------------------
    # 선택 UI
    # -------------------------------------------------------
    st.sidebar.header("필터")

    # 날짜 (2025년 10월만)
    sel_date = st.sidebar.date_input(
        "날짜 선택",
        min_value=datetime(2025, 10, 1),
        max_value=datetime(2025, 10, 31),
        value=datetime(2025, 10, 1)
    ).date()

    # 호선
    if cols["line"]:
        lines = sorted(df[cols["line"]].dropna().astype(str).unique())
    else:
        lines = ["전체"]

    sel_line = st.sidebar.selectbox("호선 선택", ["전체"] + lines)

    # -------------------------------------------------------
    # 데이터 필터링
    # -------------------------------------------------------
    filtered = df.copy()

    if cols["date"]:
        filtered = filtered[filtered[cols["date"]].dt.date == sel_date]

    if sel_line != "전체" and cols["line"]:
        filtered = filtered[filtered[cols["line"]].astype(str) == sel_line]

    # 승하차 합계 계산
    if cols["boarding"] and cols["alighting"]:
        filtered[cols["boarding"]] = pd.to_numeric(filtered[cols["boarding"]], errors="coerce").fillna(0)
        filtered[cols["alighting"]] = pd.to_numeric(filtered[cols["alighting"]], errors="coerce").fillna(0)

        filtered["sum"] = filtered[cols["boarding"]] + filtered[cols["alighting"]]
    else:
        st.error("승차/하차 컬럼을 찾을 수 없습니다.")
        st.stop()

    # 역 기준 그룹
    station_col = cols["station"] if cols["station"] else filtered.columns[0]

    top10 = (
        filtered.groupby(station_col)["sum"]
        .sum()
        .reset_index()
        .sort_values("sum", ascending=False)
        .head(10)
    )

    if top10.empty:
        st.warning("해당 조건의 데이터가 존재하지 않습니다.")
        st.stop()

    # -------------------------------------------------------
    # Plotly 그래프
    # -------------------------------------------------------
    st.subheader("승하차 합계 상위 10개 역")

    colors = make_color_list(len(top10))

    fig = go.Figure(
        data=go.Bar(
            x=top10[station_col],
            y=top10["sum"],
            marker=dict(color=colors),
            hovertemplate="%{x}<br>승하차: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        template="simple_white",
        xaxis_title="역명",
        yaxis_title="승하차 합계",
        margin=dict(l=30, r=20, t=40, b=140),
        height=500
    )

    fig.update_xaxes(tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)
