import streamlit as st

# MBTI 기반 영화/책 추천 Streamlit 앱
# 외부 라이브러리 없이 기본 라이브러리와 streamlit만 사용합니다.

MBTI_RECS = {
    "INTJ": {
        "movies": [
            ("Inception (2010)", "복잡한 구조와 아이디어 중심의 스토리 — INTJ의 전략적 사고에 어울려요."),
            ("The Imitation Game (2014)", "논리적 문제 해결과 내면의 갈등을 다룬 전기 드라마 — 계획형 성향에 추천.")
        ],
        "books": [
            ("Foundation - Isaac Asimov", "거대한 계획과 예측을 다루는 SF 걸작 — 큰 그림을 보는 INTJ에게 찰떡."),
            ("Thinking, Fast and Slow - Daniel Kahneman", "사고의 메커니즘을 분석하는 책 — 논리적 성찰을 좋아하는 분께.")
        ]
    },
    "INTP": {
        "movies": [
            ("The Social Network (2010)", "아이디어와 논쟁, 분석적 캐릭터가 매력적인 영화."),
            ("Primer (2004)", "저예산이지만 사고실험 가득한 시간여행 이야기 — 개념적 호기심을 자극합니다.")
        ],
        "books": [
            ("Gödel, Escher, Bach - Douglas Hofstadter", "메타적 사고와 연결성을 즐기는 INTP에게 명작."),
            ("The Structure of Scientific Revolutions - Thomas S. Kuhn", "사상과 패러다임 전환에 대한 통찰.")
        ]
    },
    "ENTJ": {
        "movies": [
            ("The Wolf of Wall Street (2013)", "야망과 리더십, 추진력을 느낄 수 있는 작품."),
            ("Moneyball (2011)", "전략과 체계로 문제를 해결하는 이야기 — ENTJ의 실행력에 공감.)")
        ],
        "books": [
            ("Good to Great - Jim Collins", "리더십과 조직 전략을 실제 사례로 풀어낸 비즈니스 필독서."),
            ("The Art of War - Sun Tzu", "전략적 사고의 고전 — 결단력 있는 리더에게.")
        ]
    },
    "ENTP": {
        "movies": [
            ("The Big Short (2015)", "아이디어로 규칙을 흔드는 캐릭터와 재치있는 전개가 ENTP에 잘 맞아요."),
            ("Catch Me If You Can (2002)", "즉흥성과 창의적 문제 해결을 즐기는 타입에게 추천.")
        ],
        "books": [
            ("Zero to One - Peter Thiel", "창업과 아이디어 창출에 관한 도전적 통찰."),
            ("The Innovator's Dilemma - Clayton M. Christensen", "혁신과 파괴적 변화에 대한 분석.")
        ]
    },
    "INFJ": {
        "movies": [
            ("Her (2013)", "감성적이고 사색적인 분위기, 인간관계의 깊이를 다루어요."),
            ("Pan's Labyrinth (2006)", "심볼과 은유가 많은 판타지 — 내면세계에 공감하는 분께.")
        ],
        "books": [
            ("The Little Prince - Antoine de Saint-Exupéry", "은유와 철학, 인간다움에 대한 따뜻한 통찰."),
            ("Man's Search for Meaning - Viktor E. Frankl", "의미를 찾는 깊은 성찰을 담은 책.")
        ]
    },
    "INFP": {
        "movies": [
            ("Eternal Sunshine of the Spotless Mind (2004)", "감정의 미묘함과 기억을 다루는 몽환적 사랑 이야기."),
            ("Amélie (2001)", "작고 섬세한 기쁨과 상상력이 가득한 영화.")
        ],
        "books": [
            ("The Alchemist - Paulo Coelho", "자아탐구와 꿈을 쫓는 이야기 — 감성적 여정에 어울려요."),
            ("Norwegian Wood - Haruki Murakami", "내면의 감정선을 섬세하게 그린 소설.")
        ]
    },
    "ENFJ": {
        "movies": [
            ("The King's Speech (2010)", "타인을 이끄는 공감과 결단의 이야기 — ENFJ 유형에 추천."),
            ("Remember the Titans (2000)", "팀워크와 리더십, 인간관계 중심의 감동 실화.")
        ],
        "books": [
            ("How to Win Friends and Influence People - Dale Carnegie", "사람을 이해하고 이끄는 기술 중심의 고전."),
            ("Daring Greatly - Brené Brown", "취약성을 통한 용기와 리더십에 관한 통찰.")
        ]
    },
    "ENFP": {
        "movies": [
            ("Into the Wild (2007)", "자유와 가능성을 좇는 모험 — ENFP의 영혼에 닿는 영화."),
            ("Big Fish (2003)", "상상력과 이야기의 힘을 노래하는 따뜻한 작품.")
        ],
        "books": [
            ("The Book Thief - Markus Zusak", "감성적 서사와 인류애를 담은 소설."),
            ("Wild - Cheryl Strayed", "자기발견과 모험을 그린 에세이적 회고록.")
        ]
    },
    "ISTJ": {
        "movies": [
            ("Bridge of Spies (2015)", "책임감과 원칙을 지키는 캐릭터 중심의 냉정한 드라마."),
            ("Lincoln (2012)", "전통과 원칙, 체계적 리더십을 다룬 전기 영화.")
        ],
        "books": [
            ("The Checklist Manifesto - Atul Gawande", "체계와 프로세스를 중시하는 사람에게 유용한 통찰."),
            ("To Kill a Mockingbird - Harper Lee", "도덕성, 책임감, 공감에 관한 고전 소설.")
        ]
    },
    "ISFJ": {
        "movies": [
            ("The Best Exotic Marigold Hotel (2011)", "돌봄과 헌신, 따뜻한 인간관계를 그린 영화."),
            ("Julie & Julia (2009)", "일상 속 헌신과 꾸준함이 만드는 변화의 이야기.")
        ],
        "books": [
            ("Pride and Prejudice - Jane Austen", "전통적 가치와 인간관계의 섬세한 묘사."),
            ("The Guernsey Literary and Potato Peel Pie Society - Mary Ann Shaffer", "사람과 관계를 소중히 여기는 이야기.")
        ]
    },
    "ESTJ": {
        "movies": [
            ("A Few Good Men (1992)", "규율과 책임, 명확한 윤리적 갈등을 다룬 법정 드라마."),
            ("Apollo 13 (1995)", "실행력과 위기 관리, 팀워크의 힘을 보여줌.")
        ],
        "books": [
            ("Extreme Ownership - Jocko Willink & Leif Babin", "책임감 있는 리더십의 실제 사례와 원칙."),
            ("The 7 Habits of Highly Effective People - Stephen R. Covey", "실용적 자기관리/리더십 고전.")
        ]
    },
    "ESFJ": {
        "movies": [
            ("The Pursuit of Happyness (2006)", "타인을 돌보고 실용적으로 돕는 이야기 — ESFJ에 따뜻하게 와닿아요."),
            ("Little Women (2019)", "가족·우정·돌봄의 가치가 중심인 작품.")
        ],
        "books": [
            ("The Help - Kathryn Stockett", "관계와 연대, 돌봄을 중심으로 한 소설."),
            ("Becoming - Michelle Obama", "공감과 사회적 책임을 강조하는 회고록.")
        ]
    },
    "ISTP": {
        "movies": [
            ("Drive (2011)", "실용적이고 침착한 문제 해결과 스타일이 매력적인 작품."),
            ("Mad Max: Fury Road (2015)", "행동 중심, 즉흥적 해결 능력을 즐기는 분께 추천.")
        ],
        "books": [
            ("The Martian - Andy Weir", "실전적 문제 해결과 유머가 공존하는 생존기."),
            ("On the Road - Jack Kerouac", "즉흥적 모험과 자유를 노래하는 고전.")
        ]
    },
    "ISFP": {
        "movies": [
            ("Call Me by Your Name (2017)", "감각적이고 섬세한 감정을 아름답게 그린 작품."),
            ("Moonlight (2016)", "미묘한 감정선을 섬세하게 포착한 영화.")
        ],
        "books": [
            ("The Secret Life of Bees - Sue Monk Kidd", "감성적 성장과 치유의 이야기."),
            ("Their Eyes Were Watching God - Zora Neale Hurston", "자기표현과 감정의 진실성을 다룬 소설.")
        ]
    },
    "ESTP": {
        "movies": [
            ("Casino (1995)", "강렬하고 행동적인 에너지, 리스크 감수의 재미."),
            ("Edge of Tomorrow (2014)", "액션과 빠른 템포, 현장감 있는 이야기.")
        ],
        "books": [
            ("No Easy Day - Mark Owen", "현장 중심의 회고록으로 리얼한 액션 감각."),
            ("The Bourne Identity - Robert Ludlum", "액션·스릴러 장르의 클래식.")
        ]
    },
    "ESFP": {
        "movies": [
            ("La La Land (2016)", "에너지 넘치고 감성적인 즐거움이 가득한 뮤지컬 영화."),
            ("The Greatest Showman (2017)", "화려함과 사람들 사이의 즐거움을 노래하는 작품.")
        ],
        "books": [
            ("Bossypants - Tina Fey", "유머와 인간미가 넘치는 자서전적 에세이."),
            ("Eat, Pray, Love - Elizabeth Gilbert", "삶의 즐거움과 경험을 쫓는 여행기.")
        ]
    }
}

st.set_page_config(page_title="MBTI 무비&북 추천 🎬📚", page_icon="✨")
st.title("야무진 MBTI 영화·책 추천 앱 ✨")
st.write("아래에서 MBTI 유형을 골라주시면, 그 유형에 어울리는 영화 2편과 책 2권을 센스 있게 추천해드릴게요. 🌿💡")

mbti = st.selectbox("MBTI 유형을 선택하세요:", list(MBTI_RECS.keys()))

if mbti:
    rec = MBTI_RECS.get(mbti)
    st.markdown(f"### {mbti}님을 위한 추천 목록 💌")

    st.markdown("**🎬 영화 추천 (2편)**")
    for title, desc in rec["movies"]:
        st.markdown(f"- **{title}** — {desc} {emoji_for_mbti(mbti)}")

    st.markdown("**📚 책 추천 (2권)**")
    for title, desc in rec["books"]:
        st.markdown(f"- **{title}** — {desc} {emoji_for_mbti(mbti)}")

    st.divider()
    st.write("원하시면 추천 이유를 더 길게 설명해드리거나, 다른 유형 비교도 해드릴게요. ✨")


# --------------------
# 헬퍼 함수: MBTI에 맞는 이모지 (간단한 매핑)
# --------------------

def emoji_for_mbti(code):
    mapping = {
        "INTJ": "🧭",
        "INTP": "🔬",
        "ENTJ": "🚀",
        "ENTP": "💡",
        "INFJ": "🕯️",
        "INFP": "🌙",
        "ENFJ": "🌱",
        "ENFP": "🎈",
        "ISTJ": "📜",
        "ISFJ": "🧶",
        "ESTJ": "🛡️",
        "ESFJ": "🤝",
        "ISTP": "🔧",
        "ISFP": "🎨",
        "ESTP": "⚡",
        "ESFP": "✨",
    }
    return mapping.get(code, "✨")

# Streamlit requires helper functions to be defined before use in some caching scenarios,
# but here it's simple. The app is self-contained and uses no external libs.


