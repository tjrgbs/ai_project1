
import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(page_title="강원랜드 외국인 분석", layout="wide")
st.title("🎰 강원랜드 외국인 국가별 일일 입장현황 분석 대시보드")

# ---------------- 유틸 함수 ----------------
def load_csv_from_bytes(b: bytes):
    """바이트를 받아서 여러 인코딩으로 시도해 판다스로 읽기"""
    if not b or len(b) == 0:
        raise pd.errors.EmptyDataError("Uploaded file is empty (0 bytes).")
    bio = io.BytesIO(b)

    # 1) UTF-8
    try:
        bio.seek(0)
        return pd.read_csv(bio, encoding="utf-8")
    except:
        pass

    # 2) CP949
    try:
        bio.seek(0)
        return pd.read_csv(bio, encoding="cp949")
    except:
        pass

    # 3) 텍스트로 디코딩해서 읽기
    text = b.decode("utf-8", errors="replace")
    return pd.read_csv(io.StringIO(text))

def validate_df(df: pd.DataFrame):
    """필수 컬럼 검사"""
    required = ["입장일자", "국가명", "외국인 입장객 수"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV에 필수 컬럼 없음: {missing}")

    df["입장일자"] = pd.to_datetime(df["입장일자"], errors="coerce")
    return df

# ---------------- 파일 업로더만 사용 ----------------
st.subheader("📁 CSV 파일을 업로드하세요")

uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

df = None

if uploaded_file is not None:
    try:
        b = uploaded_file.read()
        df = load_csv_from_bytes(b)
        df = validate_df(df)
        st.success("CSV 파일을 성공적으로 불러왔습니다.")
    except Exception as e:
        st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
        st.stop()
else:
    st.info("CSV 파일을 업로드하면 분석을 시작합니다.")
    st.stop()

# 숫자형 변환
df["외국인 입장객 수"] = pd.to_numeric(df["외국인 입장객 수"], errors="coerce").fillna(0).astype(int)

# ---------------- 데이터 표시 ----------------
st.subheader("📌 원본 데이터")
st.dataframe(df)

st.subheader("📊 기본 통계")
st.write(df.describe(include="all"))

# ---------------- 국가별 TOP 10 ----------------
st.subheader("🌍 국가별 총 방문객 수 TOP 10")
country_sum = df.groupby("국가명")["외국인 입장객 수"].sum().reset_index()
top10 = country_sum.sort_values("외국인 입장객 수", ascending=False).head(10)

bar = alt.Chart(top10).mark_bar().encode(
    x=alt.X("국가명:N", sort=None),
    y="외국인 입장객 수:Q",
    tooltip=["국가명", "외국인 입장객 수"]
)
st.altair_chart(bar, use_container_width=True)

# ---------------- 일자별 총 방문객 변화 ----------------
st.subheader("📅 일자별 총 방문객 수 변화")
daily = df.groupby("입장일자")["외국인 입장객 수"].sum().reset_index()

area = alt.Chart(daily).mark_area().encode(
    x="입장일자:T",
    y="외국인 입장객 수:Q"
)
st.altair_chart(area, use_container_width=True)

# ---------------- 특정 국가 선택 ----------------
st.subheader("📌 특정 국가 선택 분석")
countries = sorted(df["국가명"].dropna().unique())
selected = st.selectbox("국가 선택", countries)

sel_df = df[df["국가명"] == selected].sort_values("입장일자")

line = alt.Chart(sel_df).mark_line(point=True).encode(
    x="입장일자:T",
    y="외국인 입장객 수:Q"
)
st.altair_chart(line, use_container_width=True)

# ---------------- 국가명 직접 검색 기능 ----------------
st.subheader("🔍 국가명 직접 검색")
search = st.text_input("국가명을 입력하세요 (예: 미국)")

if search:
    if search in df["국가명"].unique():
        sdf = df[df["국가명"] == search]

        total = int(sdf["외국인 입장객 수"].sum())
        st.write(f"### ✔ 총 방문객 수: **{total}명**")

        st.write("📅 일자별 방문자 수")
        st.dataframe(sdf[["입장일자", "외국인 입장객 수"]])

        maxrow = sdf.loc[sdf["외국인 입장객 수"].idxmax()]
        minrow = sdf.loc[sdf["외국인 입장객 수"].idxmin()]

        st.write(f"🔥 최대 방문일: {maxrow['입장일자'].date()} — {int(maxrow['외국인 입장객 수'])}명")
        st.write(f"🧊 최소 방문일: {minrow['입장일자'].date()} — {int(minrow['외국인 입장객 수'])}명")

        trend = alt.Chart(sdf).mark_line(point=True).encode(
            x="입장일자:T",
            y="외국인 입장객 수:Q"
        )
        st.altair_chart(trend, use_container_width=True)
    else:
        st.warning("해당 국가는 데이터에 없습니다.")
