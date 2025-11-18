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
    # 시도 1: utf-8
    try:
        bio.seek(0)
        return pd.read_csv(bio, encoding="utf-8")
    except Exception:
        pass
    # 시도 2: cp949 (euc-kr)
    try:
        bio.seek(0)
        return pd.read_csv(bio, encoding="cp949")
    except Exception:
        pass
    # 시도 3: 텍스트로 디코딩(깨지는 문자 대체) 후 읽기
    try:
        text = b.decode("utf-8", errors="replace")
        return pd.read_csv(io.StringIO(text))
    except Exception as e:
        raise e

def load_csv_from_url(url: str):
    """URL에서 직접 읽기 (GitHub raw 등). 인코딩 시도 포함"""
    try:
        return pd.read_csv(url, encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(url, encoding="cp949")
        except Exception as e:
            raise e

def validate_df(df: pd.DataFrame):
    """필수 컬럼이 있는지 검사하고 입장일자 파싱"""
    required = ["입장일자", "국가명", "외국인 입장객 수"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV에 필수 컬럼이 없습니다: {missing}. (필수: {required})")
    # 날짜 파싱 (에러는 NaT로)
    df["입장일자"] = pd.to_datetime(df["입장일자"], errors="coerce")
    if df["입장일자"].isna().all():
        st.warning("입장일자 컬럼이 존재하나 전부 날짜로 변환되지 않았습니다. (format 문제)")
    return df

# ---------------- 입력 UI ----------------
st.markdown("업로드할 CSV 파일을 선택하거나, GitHub raw 파일 URL을 입력하세요.")
col1, col2 = st.columns([2, 3])

with col1:
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"], accept_multiple_files=False)

with col2:
    url_input = st.text_input("또는 GitHub raw URL 입력 (선택)", value="")

# ---------------- 데이터 로드 ----------------
df = None

# 우선 세션에 이미 데이터 있으면 그것을 사용 (리로드 안전)
if "df_cached" in st.session_state and st.session_state["df_cached"] is not None:
    df = st.session_state["df_cached"]

# URL이 입력되었고 아직 df가 없으면 URL로 시도
if df is None and url_input:
    try:
        with st.spinner("URL에서 CSV를 불러오는 중..."):
            df = load_csv_from_url(url_input.strip())
            df = validate_df(df)
            st.session_state["df_cached"] = df
            st.success("URL에서 CSV를 성공적으로 불러왔습니다.")
    except pd.errors.EmptyDataError:
        st.error("URL의 파일이 비어 있습니다.")
    except Exception as e:
        st.error(f"URL에서 CSV를 읽는 중 오류 발생: {e}")

# 업로드 파일이 있으면 업로더 우선
if uploaded_file is not None:
    try:
        # 안전하게 바이트 읽기
        b = uploaded_file.read()
        if b is None or len(b) == 0:
            st.error("업로드한 파일이 비어 있습니다. 다른 파일을 시도하세요.")
        else:
            with st.spinner("업로드 파일을 읽는 중..."):
                df = load_csv_from_bytes(b)
                df = validate_df(df)
                st.session_state["df_cached"] = df
                st.success("파일 업로드 및 파싱 성공.")
    except pd.errors.EmptyDataError:
        st.error("업로드한 파일이 비어 있습니다 (EmptyDataError).")
    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"파일을 읽는 도중 오류가 발생했습니다: {e}")

# ---------------- df 준비 완료 후 UI ----------------
if df is None:
    st.info("왼쪽에서 CSV를 업로드하거나 오른쪽에 GitHub raw URL을 입력하세요.")
    st.stop()

# 안전: 외국인 입장객 수를 숫자로 변환
df["외국인 입장객 수"] = pd.to_numeric(df["외국인 입장객 수"], errors="coerce").fillna(0).astype(int)

# ---- 원본 데이터 보기 ----
st.subheader("📌 원본 데이터 (샘플)")
st.dataframe(df.head(200))

# ---- 기본 통계 ----
st.subheader("📊 기본 통계")
st.write(df.describe(include="all"))

# ---- 국가별 TOP10 ----
st.subheader("🌍 국가별 총 방문객 수 TOP 10")
country_sum = df.groupby("국가명", dropna=False)["외국인 입장객 수"].sum().reset_index()
top10 = country_sum.sort_values("외국인 입장객 수", ascending=False).head(10)
bar = alt.Chart(top10).mark_bar().encode(
    x=alt.X("국가명:N", sort=None),
    y="외국인 입장객 수:Q",
    tooltip=["국가명", "외국인 입장객 수"]
)
st.altair_chart(bar, use_container_width=True)

# ---- 일자별 총합 ----
st.subheader("📅 일자별 총 방문객 수")
daily = df.groupby("입장일자")["외국인 입장객 수"].sum().reset_index()
area = alt.Chart(daily).mark_area().encode(
    x="입장일자:T",
    y="외국인 입장객 수:Q"
)
st.altair_chart(area, use_container_width=True)

# ---- 특정 국가 선택 ----
st.subheader("📌 특정 국가 선택 분석")
countries = sorted(df["국가명"].dropna().unique())
selected = st.selectbox("국가 선택", countries, index=0 if len(countries)>0 else None)

if selected:
    sel_df = df[df["국가명"] == selected].sort_values("입장일자")
    st.write(f"### 📈 {selected} 방문객 추이 (총 {sel_df['외국인 입장객 수'].sum()}명)")
    st.dataframe(sel_df[["입장일자", "외국인 입장객 수"]].reset_index(drop=True), height=300)
    line = alt.Chart(sel_df).mark_line(point=True).encode(
        x="입장일자:T",
        y="외국인 입장객 수:Q",
        tooltip=["입장일자", "외국인 입장객 수"]
    )
    st.altair_chart(line, use_container_width=True)

# ---- 국가명 직접 검색 기능 ----
st.subheader("🔍 국가명 직접 검색")
search = st.text_input("국가명을 직접 입력하세요 (예: 미국)")

if search:
    if search in df["국가명"].values:
        sdf = df[df["국가명"] == search].sort_values("입장일자")
        total = int(sdf["외국인 입장객 수"].sum())
        st.write(f"**{search} 총 방문객 수:** {total}명")
        st.dataframe(sdf[["입장일자", "외국인 입장객 수"]].reset_index(drop=True))
        # 최대/최소
        if not sdf.empty:
            maxrow = sdf.loc[sdf["외국인 입장객 수"].idxmax()]
            minrow = sdf.loc[sdf["외국인 입장객 수"].idxmin()]
            st.write(f"- 🔥 최대 방문일: {maxrow['입장일자'].date()} — {int(maxrow['외국인 입장객 수'])}명")
            st.write(f"- 🧊 최소 방문일: {minrow['입장일자'].date()} — {int(minrow['외국인 입장객 수'])}명")
            trend = alt.Chart(sdf).mark_line(point=True).encode(x="입장일자:T", y="외국인 입장객 수:Q", tooltip=["입장일자","외국인 입장객 수"])
            st.altair_chart(trend, use_container_width=True)
    else:
        st.warning("해당 국가가 데이터에 없습니다. 국가명 철자(공백/대소문자)를 확인하세요.")

st.markdown("---")
st.caption("앱 실행 중 문제가 계속되면 `app.py`가 레포 최상위에 있는지, 업로드한 CSV가 실제로 내용이 있는지(빈 파일 아님)를 다시 확인해 주세요.")
