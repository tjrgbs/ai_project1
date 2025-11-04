
import streamlit as st

# 🌸 제목
st.title("🌈 MBTI로 보는 찰떡 진로 추천 💼✨")

st.write("안녕하세요 ☀️ 오늘도 반짝이는 당신을 위한 맞춤 진로 추천 타임이에요 💖")
st.write("아래에서 당신의 MBTI를 선택해보세요 👇")

# MBTI 리스트
mbti_list = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

# 선택 상자
selected_mbti = st.selectbox("🌷 당신의 MBTI는 무엇인가요?", mbti_list)

# MBTI별 진로 추천 데이터
career_dict = {
    "INTJ": ["🧠 데이터 사이언티스트", "🗺️ 전략 컨설턴트"],
    "INTP": ["🔬 연구원", "💻 소프트웨어 개발자"],
    "ENTJ": ["🏢 경영 컨설턴트", "🚀 프로젝트 매니저"],
    "ENTP": ["💡 기업가", "📈 마케팅 전략가"],
    "INFJ": ["💬 심리상담가", "📚 작가"],
    "INFP": ["🎨 예술가", "🌿 사회복지사"],
    "ENFJ": ["🍎 교육자", "🤝 인사 관리자"],
    "ENFP": ["🎥 콘텐츠 크리에이터", "🎯 광고 기획자"],
    "ISTJ": ["📊 회계사", "🏛️ 공무원"],
    "ISFJ": ["💉 간호사", "🍀 초등교사"],
    "ESTJ": ["👩‍💼 팀 리더", "🏗️ 운영 관리자"],
    "ESFJ": ["💌 고객 서비스 매니저", "🗂️ 행정 직원"],
    "ISTP": ["🔧 엔지니어", "🚗 정비 기술자"],
    "ISFP": ["🎨 디자이너", "📸 사진작가"],
    "ESTP": ["💼 세일즈 매니저", "🎉 이벤트 플래너"],
    "ESFP": ["🎤 배우", "🌟 홍보 담당자"]
}

# 결과 출력
if selected_mbti:
    st.markdown("---")
    st.subheader(f"💫 {selected_mbti} 유형에게 어울리는 진로는 바로... 💫")
    careers = career_dict[selected_mbti]
    st.success(f"✨ 1️⃣ {careers[0]}")
    st.success(f"🌈 2️⃣ {careers[1]}")
    st.markdown("---")
    st.caption("💌 당신의 개성과 열정이 반짝이는 길을 응원해요 🌟")
