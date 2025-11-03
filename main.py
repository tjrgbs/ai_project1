import streamlit as st
st.title('나의 첫 웹 서비스 만들기!!')
name=st.text_input('이름을 임력하세요')
menu-st,selectbox('좋아하시는 음식을 선택해주세요:',[이현맘',이현빠')
if st.button('인사말 생성'):
  st.write(name+' 주인님! 안녕하세요!')
  st.warning('방가방가!')
  st.error('혼또니 반갑다데스')
          st.balloons()
