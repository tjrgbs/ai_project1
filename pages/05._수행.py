import streamlit as st
import pandas as pd
import altair as alt

# 파일 업로드
st.title("강원랜드 외국인 국가별 일일 입장현황 분석 대시보드")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"]) 

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        df = pd.read_csv(uploaded_file, encoding="cp949")

    st.subheader("📌 Raw Data")
    st.dataframe(df)

    # 기본 통계
    st.subheader("📊 기본 통계 분석")
    st.write(df.describe(include='all'))

    # 날짜 변환
    df['입장일자'] = pd.to_datetime(df['입장일자'])

    # 국가 선택
    countries = sorted(df['국가명'].unique())
    selected_country = st.selectbox("국가 선택", countries)

    filtered = df[df['국가명'] == selected_country]

    st.subheader(f"📈 {selected_country} 일자별 입장객 수 추세")
    chart = alt.Chart(filtered).mark_line().encode(
        x='입장일자:T',
        y='외국인 입장객 수:Q'
    )
    st.altair_chart(chart, use_container_width=True)

    # 국가별 총합
    st.subheader("🌍 국가별 총 방문객 수 TOP 10")
    country_sum = df.groupby('국가명')['외국인 입장객 수'].sum().reset_index()
    top_10 = country_sum.sort_values(by='외국인 입장객 수', ascending=False).head(10)

    bar_chart = alt.Chart(top_10).mark_bar().encode(
        x='국가명:N',
        y='외국인 입장객 수:Q',
        tooltip=['국가명', '외국인 입장객 수']
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # 일자별 총합
    st.subheader("📅 일자별 총 방문객 수 변화")
    daily_sum = df.groupby('입장일자')['외국인 입장객 수'].sum().reset_index()

    daily_chart = alt.Chart(daily_sum).mark_area().encode(
        x='입장일자:T',
        y='외국인 입장객 수:Q'
    )
    st.altair_chart(daily_chart, use_container_width=True)

        # 국가 이름 직접 입력하여 상세 방문객 정보 조회
    st.subheader("🔍 국가명 검색 기능")
    input_country = st.text_input("국가명을 입력하세요 (예: 미국, 일본)")

    if input_country:
        st.subheader(f"📘 '{input_country}' 분석 결과")
        # 존재 여부 체크
        if input_country in df['국가명'].unique():
            country_df = df[df['국가명'] == input_country]

            # 총 방문객 수
            total_visitors = int(country_df['외국인 입장객 수'].sum())
            st.write(f"**총 방문객 수:** {total_visitors}명")

            # 일자별 방문 현황
            st.write("### 📅 일자별 방문객 수")
            st.dataframe(country_df[['입장일자','외국인 입장객 수']].sort_values('입장일자'))

            # 가장 많이 방문한 날짜
            max_row = country_df.loc[country_df['외국인 입장객 수'].idxmax()]
            st.write(f"### 🔥 최대 방문일
- 날짜: **{max_row['입장일자'].date()}**
- 방문객 수: **{int(max_row['외국인 입장객 수'])}명**")

            # 최소 방문일
            min_row = country_df.loc[country_df['외국인 입장객 수'].idxmin()]
            st.write(f"### 🧊 최소 방문일
- 날짜: **{min_row['입장일자'].date()}**
- 방문객 수: **{int(min_row['외국인 입장객 수'])}명**")

            # 해당 국가 그래프
            st.write("### 📈 방문객 수 추세 그래프")
            line_chart = alt.Chart(country_df).mark_line().encode(
                x='입장일자:T',
                y='외국인 입장객 수:Q'
            )
            st.altair_chart(line_chart, use_container_width=True)

        else:
            st.warning("해당 국가가 데이터에 존재하지 않습니다.")
        if input_country in df['국가명'].unique():
            total_visitors = int(df[df['국가명'] == input_country]['외국인 입장객 수'].sum())
            st.write(f"**{input_country} 총 방문객 수:** {total_visitors}명")
        else:
            st.warning("해당 국가가 데이터에 존재하지 않습니다.")

    st.success("분석 완료!")

else:
    st.info("CSV 파일을 업로드하면 분석이 시작됩니다.")
