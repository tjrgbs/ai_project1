import streamlit as st
import pandas as pd
import altair as alt

# ---------------- 기본 설정 ----------------
st.set_page_config(page_title="강원랜드 외국인 분석", layout="wide")
st.title("🎰 강원랜드 외국인 국가별 일일 입장현황 분석 대시보드")

# ---------------- 파일 업로더 ----------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    # 인코딩 자동 처리
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        df = pd.read_csv(uploaded_file, encoding="cp949")

    # 날짜 변환
    df['입장일자'] = pd.to_datetime(df['입장일자'])

    # ---------------- 원본 데이터 ----------------
    st.subheader("📌 원본 데이터")
    st.dataframe(df)

    # ---------------- 기본 통계 ----------------
    st.subheader("📊 기본 통계 분석")
    st.write(df.describe(include='all'))

    # ---------------- 국가별 TOP10 ----------------
    st.subheader("🌍 국가별 총 방문객 수 TOP 10")
    country_sum = df.groupby('국가명')['외국인 입장객 수'].sum().reset_index()
    top10 = country_sum.sort_values('외국인 입장객 수', ascending=False).head(10)

    bar = alt.Chart(top10).mark_bar().encode(
        x='국가명:N',
        y='외국인 입장객 수:Q',
        tooltip=['국가명', '외국인 입장객 수']
    )
    st.altair_chart(bar, use_container_width=True)

    # ---------------- 일자별 총 방문객 ----------------
    st.subheader("📅 일자별 총 방문객 수 변화")
    daily = df.groupby('입장일자')['외국인 입장객 수'].sum().reset_index()

    area = alt.Chart(daily).mark_area().encode(
        x='입장일자:T',
        y='외국인 입장객 수:Q'
    )
    st.altair_chart(area, use_container_width=True)

    # ---------------- 국가 선택 ----------------
    st.subheader("📌 특정 국가 선택 분석")
    country_list = sorted(df['국가명'].unique())
    selected = st.selectbox("국가 선택", country_list)

    sel_df = df[df['국가명'] == selected]

    line = alt.Chart(sel_df).mark_line().encode(
        x='입장일자:T',
        y='외국인 입장객 수:Q'
    )
    st.altair_chart(line, use_container_width=True)

    # ---------------- 국가 이름 직접 입력 기능 ----------------
    st.subheader("🔍 국가명 직접 검색")
    search = st.text_input("국가명을 입력하세요 (예: 미국)")

    if search:
        st.write(f"### 📘 '{search}' 분석 결과")

        if search in df['국가명'].unique():
            sdf = df[df['국가명'] == search]

            total = int(sdf['외국인 입장객 수'].sum())
            st.write(f"### ✔ 총 방문객 수: **{total}명**")

            st.write("### 📅 일자별 방문자 수")
            st.dataframe(sdf[['입장일자', '외국인 입장객 수']].sort_values('입장일자'))

            maxrow = sdf.loc[sdf['외국인 입장객 수'].idxmax()]
            st.write(f"### 🔥 최대 방문일: {maxrow['입장일자'].date()} — **{int(maxrow['외국인 입장객 수'])}명**")

            minrow = sdf.loc[sdf['외국인 입장객 수'].idxmin()]
            st.write(f"### 🧊 최소 방문일: {minrow['입장일자'].date()} — **{int(minrow['외국인 입장객 수'])}명**")

            trend = alt.Chart(sdf).mark_line().encode(
                x='입장일자:T',
                y='외국인 입장객 수:Q'
            )
            st.altair_chart(trend, use_container_width=True)
        else:
            st.warning("해당 국가가 데이터에 없습니다.")

else:
    st.info("CSV 파일을 업로드하면 분석이 시작됩니다.")
