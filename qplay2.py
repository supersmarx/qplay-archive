import streamlit as st
import pandas as pd
import json
import os

# 1. 페이지 설정 및 제목 스타일링
st.set_page_config(page_title="Qplay 연상퀴즈 족보 v2.0", layout="wide")

# CSS를 활용한 제목 및 서브타이틀 디자인
st.markdown("""
    <style>
    .main-title {
        font-size: 50px !important;
        font-weight: bold;
        color: #1E1E1E;
        margin-bottom: -10px;
    }
    .sub-title {
        font-size: 16px !important;
        color: #666666;
        margin-bottom: 30px;
    }
    </style>
    <p class="main-title">연상퀴즈 족보 v2.0</p>
    <p class="sub-title">제시어로 정답을 빠르게 찾는 아카이브</p>
    """, unsafe_allow_html=True)

# 2. 비밀번호 보안 기능 (접속자 제한)
def check_password():
    """사용자가 올바른 비밀번호를 입력했는지 확인합니다."""
    def password_entered():
        if st.session_state["password"] == "1234":  # <--- 여기에 사용할 비밀번호를 설정하세요!
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("접속 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("비밀번호가 틀렸습니다. 다시 입력하세요", type="password", on_change=password_entered, key="password")
        st.error("😕 접근 권한이 없습니다.")
        return False
    else:
        return True

if check_password():
    # --- 비밀번호 통과 시 아래 앱 내용이 표시됩니다 ---

    # 이미지 배치
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists('logo.jpg'):
            st.image('logo.jpg', width=120)
    with col2:
        if os.path.exists('deco.jpg'):
            st.image('deco.jpg', use_container_width=True)

    # 데이터 로드
    DB_FILE = 'quizdata.json'
    def load_data():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(data):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    data = load_data()
    df = pd.DataFrame(data)

    # 다중 키워드 검색 (공백 구분)
    st.sidebar.header("🔍 검색")
    search_query = st.sidebar.text_input("검색어 입력 (공백으로 다중 검색 가능)", "")

    filtered_df = df.copy()
    if search_query:
        keywords = search_query.split()
        for kw in keywords:
            filtered_df = filtered_df[
                filtered_df['answer'].str.contains(kw, case=False) | 
                filtered_df['keywords'].apply(lambda x: any(kw.lower() in str(i).lower() for i in x))
            ]

    # 결과 테이블
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # 데이터 관리 익스팬더
    with st.expander("➕ 새 족보 추가 / 수정"):
        new_ans = st.text_input("정답")
        new_kws = st.text_input("연상 단어 (쉼표로 구분)")
        if st.button("저장하기"):
            if new_ans:
                data.append({"answer": new_ans, "keywords": [k.strip() for k in new_kws.split(",") if k.strip()]})
                save_data(data)
                st.rerun()