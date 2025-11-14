# streamlit_mbti_app.py
# Streamlit app: 국가별 MBTI 비율 시각화 (Plotly 인터랙티브)
# 설명: CSV 업로드 또는 /mnt/data/countriesMBTI_16types.csv 파일 사용
# 사용법: streamlit run streamlit_mbti_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Country MBTI Explorer", layout="wide")

MBTI_COLUMNS = ['INFJ','ISFJ','ISTJ','INTJ','INFP','ISFP','ISTP','INTP',
                'ENFJ','ESFJ','ESTJ','ENTJ','ENFP','ESFP','ESTP','ENTP']

@st.cache_data
def load_csv_from_path(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_csv_from_buffer(buffer) -> pd.DataFrame:
    df = pd.read_csv(buffer)
    return df

# Utility: interpolate between two hex colors
def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def interp_hex(c1, c2, t: float):
    r1,g1,b1 = hex_to_rgb(c1)
    r2,g2,b2 = hex_to_rgb(c2)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return rgb_to_hex((r,g,b))

# Create color list: 1st -> red, others -> blue gradient from deep to pale
def make_colors_by_rank(n:int):
    colors = []
    if n <= 0:
        return colors
    red = '#E63946'  # top
    deep_blue = '#0d6efd'  # 2nd color start
    light_blue = '#e7f0ff' # fade to

    colors.append(red)
    if n == 1:
        return colors

    # For positions 2..n, compute gradient t from 0..1
    for i in range(1, n):
        # normalized position: 0 -> i=1 (2nd place) should be deep, i=n-1 -> light
        t = (i-1) / max(1, (n-2)) if n>2 else 0
        colors.append(interp_hex(deep_blue, light_blue, t))
    return colors

# Load data: offer uploader or default path
st.title("🌍 Country MBTI Explorer — Plotly + Streamlit")
st.markdown("앱: 국가를 선택하면 해당 국가의 MBTI 비율을 인터랙티브 막대그래프로 표시합니다.")

with st.sidebar:
    st.header("데이터 입력")
    uploaded = st.file_uploader("CSV 파일 업로드 (열: Country + 16 MBTI columns)", type=['csv'])
    use_example = st.checkbox('Use bundled example (if exists at /mnt/data/countriesMBTI_16types.csv)', value=True)

# Load dataframe
df = None
if uploaded is not None:
    try:
        df = load_csv_from_buffer(uploaded)
    except Exception as e:
        st.error(f"업로드한 파일을 읽는 중 오류가 발생했습니다: {e}")

if df is None and use_example:
    try:
        df = load_csv_from_path('/mnt/data/countriesMBTI_16types.csv')
    except Exception:
        df = None

if df is None:
    st.warning("데이터를 제공해주세요. 좌측에서 CSV 파일을 업로드하거나, /mnt/data/countriesMBTI_16types.csv가 존재하는지 확인하세요.")
    st.stop()

# Basic validation and cleanup
if 'Country' not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다. 파일을 확인하세요.")
    st.stop()

# Ensure MBTI columns exist (case-insensitive match)
cols_lower = [c.lower() for c in df.columns]
mbti_map = {}
for mb in MBTI_COLUMNS:
    if mb.lower() in cols_lower:
        mbti_map[mb] = df.columns[cols_lower.index(mb.lower())]
    else:
        mbti_map[mb] = None

missing = [mb for mb,v in mbti_map.items() if v is None]
if missing:
    st.warning(f"다음 MBTI 열이 파일에 없습니다: {missing}. 일부 기능이 제한될 수 있습니다.")

# Build normalized dataframe with Country and available MBTI cols
avail_mbti = [mb for mb,v in mbti_map.items() if v is not None]
plot_df = df[['Country'] + [mbti_map[mb] for mb in avail_mbti]].copy()
# Rename columns to standardized MBTI codes
rename_map = {mbti_map[mb]: mb for mb in avail_mbti}
plot_df = plot_df.rename(columns=rename_map)

# Fill NaN with zeros (or warn?)
plot_df[avail_mbti] = plot_df[avail_mbti].fillna(0)

# Sidebar: country select
countries = plot_df['Country'].astype(str).tolist()
selected_country = st.sidebar.selectbox('국가 선택', countries)

# Extract row
row = plot_df[plot_df['Country'].astype(str) == str(selected_country)]
if row.empty:
    st.error('선택한 국가의 데이터가 없습니다.')
    st.stop()

row = row.iloc[0]
# Build series of MBTI -> value
values = {mb: float(row[mb]) for mb in avail_mbti}
# If values look like proportions >1, detect and normalize
max_val = max(values.values()) if values else 0
if max_val > 1.1:
    st.info('데이터 값이 percent(0-100) 형태로 보입니다. 100기준에서 비율(0-1)로 자동 변환합니다.)')
    values = {k: v/100.0 for k,v in values.items()}

# Create DataFrame for plotting (sorted by value desc)
plot_series = pd.Series(values).sort_values(ascending=False)
plot_series = plot_series.reset_index()
plot_series.columns = ['MBTI','Ratio']
plot_series['Pct'] = (plot_series['Ratio']*100).round(2)

# Colors by rank
colors = make_colors_by_rank(len(plot_series))

# Create Plotly figure (bars sorted by Ratio desc)
fig = go.Figure()
fig.add_trace(go.Bar(
    x=plot_series['MBTI'],
    y=plot_series['Ratio'],
    text=plot_series['Pct'].astype(str) + '%',
    textposition='auto',
    marker=dict(color=colors, line=dict(width=0.5, color='rgba(0,0,0,0.1)')),
    hovertemplate='<b>%{x}</b><br>비율: %{y:.4f} (%{text})<extra></extra>'
))

fig.update_layout(
    title=f"{selected_country} — MBTI 비율 (상위부터 정렬)",
    yaxis=dict(title='비율 (0-1)', tickformat='.2f'),
    xaxis=dict(title='MBTI 유형'),
    template='simple_white',
    margin=dict(l=40, r=20, t=70, b=40),
    height=520
)

# Show top summary
top_mbti = plot_series.iloc[0]
st.markdown(f"### {selected_country} — 가장 높은 MBTI: **{top_mbti['MBTI']}** ({top_mbti['Pct']}%)")

st.plotly_chart(fig, use_container_width=True)

# Optional: show raw data table
with st.expander('원본 데이터 보기'):
    st.dataframe(row[ ['Country'] + avail_mbti ])

# Footer: tips
st.markdown("---")
st.markdown("**팁:** CSV 파일의 MBTI 값이 0~1 사이 비율인지(예: 0.05), 아니면 0~100 퍼센트인지(예: 5 또는 12.3) 확인하세요. 이 앱은 100기준으로 보이면 자동으로 0~1로 변환합니다.")

# --- Requirements (save as requirements.txt) ---
# 아래 내용을 requirements.txt로 저장하세요.
# streamlit
# pandas
# plotly
# numpy

# End of file
