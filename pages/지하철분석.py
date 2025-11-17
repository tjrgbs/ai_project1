# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime
import chardet
from io import BytesIO

st.set_page_config(page_title="지하철 상위역 시각화 (2025-10)", layout="wide")

st.title("🚇 2025년 10월 — 호선별 상위 10개역 (승차+하차 합계)")
st.markdown(
    "CSV 파일을 업로드하거나 `/mnt/data/wnlgkcjf.csv` (서버에 존재하면 자동 로드)를 사용합니다. "
    "날짜와 호선을 선택하면 해당 조건에서 승하차 합계가 큰 역 상위 10개를 보여줍니다."
)

@st.cache_data
def detect_encoding_and_read(path_or_bytes):
    # path_or_bytes: path string or bytes-like from uploader
    if isinstance(path_or_bytes, str):
        raw = open(path_or_bytes, "rb").read(20000)
    else:
        raw = path_or_bytes.read(20000)
        path_or_bytes.seek(0)
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    # read fully
    if isinstance(path_or_bytes, str):
        df = pd.read_csv(path_or_bytes, encoding=enc)
    else:
        df = pd.read_csv(path_or_bytes, encoding=enc)
    return df

def guess_columns(df):
    cols = [c.lower() for c in df.columns]
    # date
    date_col = None
    for cand in ["사용일자","일자","date","날짜","등록일"]:
        for c in df.columns:
            if cand in c.lower():
                date_col = c
                break
        if date_col: break
    # line
    line_col = None
    for cand in ["호선","line"]:
        for c in df.columns:
            if cand in c.lower():
                line_col = c
                break
        if line_col: break
    # station
    station_col = None
    for cand in ["역명","역","station","station_name","역사"]:
        for c in df.columns:
            if cand in c.lower():
                station_col = c
                break
        if station_col: break
    # boarding / alighting
    boarding_col = None
    alighting_col = None
    for c in df.columns:
        lc = c.lower()
        if "승차" in lc or "boarding" in lc:
            if boarding_col is None:
                boarding_col = c
        if "하차" in lc or "alight" in lc or "alighting" in lc:
            if alighting_col is None:
                alighting_col = c
    # fallback: numeric columns - try to find two numeric columns likely to be boarding/hc
    numeric_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
    if boarding_col is None or alighting_col is None:
        # If numeric_cols >=2, choose last two
        if len(numeric_cols) >= 2:
            if boarding_col is None:
                boarding_col = numeric_cols[-2]
            if alighting_col is None:
                alighting_col = numeric_cols[-1]
    return {
        "date": date_col,
        "line": line_col,
        "station": station_col,
        "boarding": boarding_col,
        "alighting": alighting_col
    }

def parse_date_column(df, date_col):
    if date_col is None:
        return df
    ser = df[date_col]
    # If already datetime
    if np.issubdtype(ser.dtype, np.datetime64):
        return df
    # Try common formats
    try:
        df[date_col] = pd.to_datetime(ser, errors='coerce', dayfirst=False)
        return df
    except Exception:
        df[date_col] = pd.to_datetime(ser.astype(str), errors='coerce', infer_datetime_format=True)
        return df

def make_color_list(n):
    # first is solid red, others: blue gradient fading (darker to lighter)
    colors = []
    if n <= 0:
        return colors
    colors.append("rgba(230,39,39,1.0)")  # red for 1st
    if n == 1:
        return colors
    # create n-1 shades from deep blue to very light blue
    start_rgb = np.array([10, 60, 160])   # deep blue-ish
    end_rgb   = np.array([180, 200, 255]) # very light blue
    steps = n - 1
    for i in range(steps):
        t = i / max(1, steps-1)  # 0..1
        rgb = (1 - t) * start_rgb + t * end_rgb
        alpha = 0.95 - 0.6 * (i / max(1, steps-1))  # slightly reduce alpha across
        r,g,b = rgb.astype(int).tolist()
        colors.append(f"rgba({r},{g},{b},{alpha:.3f})")
    return colors

# Load data: either file uploader or default path
uploaded = st.file_uploader("CSV 파일 업로드 (선택). 인코딩 자동 감지합니다.", type=["csv"])
default_path = "/mnt/data/wnlgkcjf.csv"
df = None
load_error = None
if uploaded is not None:
    try:
        df = detect_encoding_and_read(uploaded)
    except Exception as e:
        load_error = f"업로드한 파일을 읽는 중 오류: {e}"
elif os.path.exists(default_path):
    st.info(f"서버에 기본 파일을 발견했습니다: `{default_path}` — 자동 로드합니다.")
    try:
        df = detect_encoding_and_read(default_path)
    except Exception as e:
        load_error = f"기본 파일을 읽는 중 오류: {e}"
else:
    st.warning("파일을 업로드하거나 `/mnt/data/wnlgkcjf.csv` 를 프로젝트 루트에 올려주세요.")

if load_error:
    st.error(load_error)

if df is not None:
    st.subheader("원본 데이터 미리보기")
    st.write(f"행: {df.shape[0]} / 열: {df.shape[1]}")
    st.dataframe(df.head(8))

    # 자동 컬럼 매핑
    cols = guess_columns(df)
    st.write("감지된 컬럼 (자동 매핑):", cols)

    df = parse_date_column(df, cols["date"])

    # 선택 UI: 날짜(2025-10-01 ~ 2025-10-31), 호선(데이터내 고유값)
    st.sidebar.header("필터")
    # date picker: limit to Oct 2025
    min_date = datetime(2025, 10, 1).date()
    max_date = datetime(2025, 10, 31).date()
    sel_date = st.sidebar.date_input("날짜 선택 (2025년 10월)", value=min_date, min_value=min_date, max_value=max_date)
    # determine lines
    if cols["line"] and cols["line"] in df.columns:
        lines = df[cols["line"]].dropna().astype(str).unique().tolist()
    else:
        # fallback: let user choose "전체"
        lines = ["전체"]
    lines = sorted(lines)
    sel_line = st.sidebar.selectbox("호선 선택", options=["전체"] + lines if "전체" not in lines else lines)

    # Filter df by date and line
    working = df.copy()
    if cols["date"] and cols["date"] in working.columns:
        working = working[ pd.to_datetime(working[cols["date"]]).dt.date == sel_date ]
    # else, no date filtering

    if sel_line and sel_line != "전체" and cols["line"] and cols["line"] in working.columns:
        working = working[ working[cols["line"]].astype(str) == str(sel_line) ]

    # ensure numeric
    bcol = cols["boarding"]
    acol = cols["alighting"]
    if bcol is None or acol is None:
        st.error("승차/하차 컬럼을 자동으로 찾지 못했습니다. CSV 컬럼명에 '승차' 또는 '하차'가 포함되어 있는지 확인해주세요.")
    else:
        # coerce to numeric
        working[bcol] = pd.to_numeric(working[bcol], errors='coerce').fillna(0).astype(int)
        working[acol] = pd.to_numeric(working[acol], errors='coerce').fillna(0).astype(int)
        working["_sum"] = working[bcol] + working[acol]

        # determine station column
        if cols["station"] and cols["station"] in working.columns:
            station_col = cols["station"]
        else:
            # fallback to first non-date/string column
            station_candidates = [c for c in working.columns if working[c].dtype == object]
            station_col = station_candidates[0] if station_candidates else working.columns[0]

        grouped = working.groupby(station_col)["_sum"].sum().reset_index().rename(columns={station_col: "station", "_sum": "total"})
        top10 = grouped.sort_values("total", ascending=False).head(10).reset_index(drop=True)

        if top10.empty:
            st.warning("선택한 조건에 해당하는 데이터가 없습니다. (날짜/호선 조합을 확인해주세요.)")
        else:
            st.subheader(f"상위 10개 역 — {sel_date} / 호선: {sel_line if sel_line else '전체'}")
            st.dataframe(top10)

            # create colors
            colors = make_color_list(len(top10))

            # Plotly bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=top10["station"],
                y=top10["total"],
                marker=dict(color=colors, line=dict(width=0)),
                hovertemplate="%{x}<br>승하차 합계: %{y}<extra></extra>"
            ))
            fig.update_layout(
                yaxis_title="승차+하차 합계",
                xaxis_title="역명",
                template="simple_white",
                margin=dict(l=40, r=20, t=60, b=120),
                height=520
            )
            # make x-axis labels vertical if many
            fig.update_xaxes(tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                """
                **색상 규칙**: 1위 역은 빨간색, 2위~10위는 파란색 계열의 그라데이션(1순위에 비해 옅어짐)입니다.
                
                **메모**:
                - 코드가 자동으로 컬럼을 추정합니다. 만약 컬럼명이 다르면 `일자/사용일자`, `호선`, `역명`, `승차`, `하차` 등의 컬럼명이 있는지 CSV를 확인해 주세요.
                - 날짜 형식이 비표준(예: YYYYMMDD 숫자)일 경우에도 pandas가 파싱 가능하면 동작합니다.
                """
            )
