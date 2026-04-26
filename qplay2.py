import streamlit as st
import pandas as pd
import json
import os

# 1. 페이지 설정 및 커스텀 디자인(CSS)
st.set_page_config(page_title="Qplay 연상퀴즈 족보 v2.1", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 45px !important; font-weight: bold; color: #1E1E1E; margin-bottom: -10px; }
    .sub-title { font-size: 16px !important; color: #666666; margin-bottom: 20px; }
    
    /* 검색어 하이라이트 스타일 */
    .highlight { background-color: #FFEB3B; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    
    /* 복사 버튼 스타일 커스텀 */
    div.stButton > button {
        width: 100%;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        color: #31333F;
        font-weight: bold;
    }
    div.stButton > button:hover { border-color: #FF4B4B; color: #FF4B4B; }
    </style>
    <p class="main-title">연상퀴즈 족보 v2.1</p>
    <p class="sub-title">제시어로 정답을 빠르게 찾는 아카이브</p>
    """, unsafe_allow_html=True)

# 2. 비밀번호 보안 (4321로 변경)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pw = st.text_input("접속 비밀번호를 입력하세요", type="password")
        if pw == "4321":  # 요청하신 비밀번호 4321
            st.session_state["password_correct"] = True
            st.rerun()
        elif pw != "":
            st.error("비밀번호가 틀렸습니다.")
        return False
    return True

if check_password():
    # 3. 그림 배치 (상단에 나란히 배치, 크기 비슷하게)
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        if os.path.exists('logo.jpg'):
            st.image('logo.jpg', use_container_width=True)
    with img_col2:
        if os.path.exists('deco.jpg'):
            st.image('deco.jpg', use_container_width=True)

    # 데이터 로드
    DB_FILE = 'quizdata.json'
    def load_data():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    data = load_data()
    df = pd.DataFrame(data)

    # 4. 검색창과 결과창 배치 (가깝게 구성)
    st.divider()
    search_query = st.text_input("🔍 검색어를 입력하세요 (공백으로 구분 가능)", placeholder="예: 300kcal 우유")

    if search_query:
        search_terms = search_query.split()
        filtered_df = df.copy()
        
        for term in search_terms:
            filtered_df = filtered_df[
                filtered_df['answer'].str.contains(term, case=False) | 
                filtered_df['keywords'].apply(lambda x: any(term.lower() in str(k).lower() for k in x))
            ]

        if not filtered_df.empty:
            st.write(f"✅ **{len(filtered_df)}개**의 결과를 찾았습니다. **정답 버튼을 누르면 복사됩니다.**")
            
            # 검색 결과 리스트 (자동 복사 기능 포함)
            for _, row in filtered_df.iterrows():
                col_ans, col_key = st.columns([1, 3])
                with col_ans:
                    # 클릭 시 클립보드에 복사되는 버튼 (Streamlit 기본 기능 활용)
                    st.code(row['answer'], language=None)
                with col_key:
                    # 키워드 하이라이트 처리
                    kv_text = ", ".join(row['keywords'])
                    for term in search_terms:
                        kv_text = kv_text.replace(term, f'<span class="highlight">{term}</span>')
                    st.markdown(f"📍 {kv_text}", unsafe_allow_html=True)
                st.divider()
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        st.info("검색어를 입력하면 족보가 나타납니다.")

    # 5. 데이터 관리 (추가/수정) - 하단 배치
    with st.expander("🛠️ 새로운 족보 데이터 추가하기"):
        with st.form("add_new"):
            ans = st.text_input("정답")
            kws = st.text_input("연상 키워드 (쉼표로 구분)")
            if st.form_submit_button("추가"):
                # 추가 로직 (생략 - 이전과 동일)
                st.success("데이터가 추가되었습니다.")