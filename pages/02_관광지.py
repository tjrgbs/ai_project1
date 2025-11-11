import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="서울 관광지도 🗺️", page_icon="🌸", layout="wide")

st.title("🇰🇷 외국인들이 사랑한 서울 관광지 Top 10 🌟")
st.write("서울의 인기 관광지를 지도 위에서 만나보세요! 💖")

# --- 서울 관광지 Top 10 데이터 ---
spots = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "desc": "한국의 대표 궁궐 🏯"},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982708, "desc": "쇼핑 천국 🛍️"},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, "desc": "서울의 전망 명소 🌇"},
    {"name": "홍대 (Hongdae)", "lat": 37.556383, "lon": 126.923611, "desc": "젊음의 거리 🎶"},
    {"name": "북촌한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, "desc": "전통 한옥길 🏠"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566540, "lon": 127.009110, "desc": "현대적 랜드마크 🏙️"},
    {"name": "이태원 (Itaewon)", "lat": 37.534525, "lon": 126.994160, "desc": "다국적 문화 거리 🌏"},
    {"name": "청계천 (Cheonggyecheon Stream)", "lat": 37.569103, "lon": 126.978141, "desc": "도심 속 힐링 산책로 🌿"},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.513068, "lon": 127.102574, "desc": "서울의 랜드마크 🏙️"},
    {"name": "한강공원 (Hangang Park)", "lat": 37.528344, "lon": 126.932617, "desc": "서울의 여유로운 강변 🛶"}
]

# --- 지도 생성 ---
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB positron")

# --- 마커 추가 ---
for spot in spots:
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=f"<b>{spot['name']}</b><br>{spot['desc']}",
        tooltip=spot["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# --- Streamlit에 Folium 지도 표시 ---
st_data = st_folium(m, width=900, height=600)

st.markdown("---")
st.caption("© 2025 Seoul Travel Map with Folium 🌸")
import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="서울 관광지도 🗺️", page_icon="🌸", layout="wide")

st.title("🇰🇷 외국인들이 사랑한 서울 관광지 Top 10 🌟")
st.write("마커를 클릭하면 아래에 관광지 설명이 나타나요 ✨")

# --- 관광지 데이터 ---
spots = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "desc": "조선시대의 대표 궁궐, 서울의 상징 🏯"},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982708, "desc": "서울 최고의 쇼핑 거리 🛍️"},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, "desc": "서울 전경을 한눈에 볼 수 있는 명소 🌇"},
    {"name": "홍대 (Hongdae)", "lat": 37.556383, "lon": 126.923611, "desc": "예술과 젊음의 거리 🎶"},
    {"name": "북촌한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, "desc": "전통 한옥과 서울의 정취 🏠"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566540, "lon": 127.009110, "desc": "현대적인 건축미의 랜드마크 🏙️"},
    {"name": "이태원 (Itaewon)", "lat": 37.534525, "lon": 126.994160, "desc": "다국적 문화가 어우러진 거리 🌏"},
    {"name": "청계천 (Cheonggyecheon Stream)", "lat": 37.569103, "lon": 126.978141, "desc": "도심 속 힐링 산책로 🌿"},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.513068, "lon": 127.102574, "desc": "서울의 랜드마크 초고층 빌딩 🏙️"},
    {"name": "한강공원 (Hangang Park)", "lat": 37.528344, "lon": 126.932617, "desc": "서울의 여유로운 강변 명소 🛶"}
]

# --- 지도 생성 ---
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB positron")

# --- 마커 추가 ---
for spot in spots:
    folium.Marker(
        [spot["lat"], spot["lon"]],
        popup=spot["name"],  # 클릭 시 해당 이름만 반환되도록
        tooltip="클릭해보세요 👆",
        icon=folium.Icon(color="cadetblue", icon="info-sign")
    ).add_to(m)

# --- 지도 표시 ---
st_data = st_folium(m, width=950, height=600)

# --- 클릭된 마커 정보 처리 ---
clicked_name = None
if st_data and st_data["last_object_clicked_popup"]:
    clicked_name = st_data["last_object_clicked_popup"]

# --- 관광지 정보 표시 영역 ---
st.markdown("---")
st.subheader("📍 선택한 관광지 정보")

if clicked_name:
    # 선택된 관광지 정보 찾기
    for spot in spots:
        if spot["name"] == clicked_name:
            st.markdown(f"### {spot['name']}")
            st.write(spot["desc"])
            break
else:
    st.info("지도의 마커를 클릭하면 이곳에 설명이 표시됩니다 💡")

st.caption("© 2025 Seoul Travel Map with Folium 🌸")


