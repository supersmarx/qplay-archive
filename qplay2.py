import streamlit as st
import pandas as pd
import json
import os
import requests
import base64

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="연상퀴즈 족보 v3.0", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 48px !important; font-weight: bold; color: #1E1E1E; margin-bottom: -10px; }
    .sub-title { font-size: 16px !important; color: #666666; margin-bottom: 25px; }
    .highlight { background-color: #FFEB3B; padding: 2px 5px; border-radius: 3px; font-weight: bold; color: black; }
    div.stButton > button { width: 100%; font-weight: bold; }
    </style>
    <p class="main-title">연상퀴즈 족보 v3.0</p>
    <p class="sub-title">제시어로 정답을 빠르게 찾는 아카이브</p>
    """, unsafe_allow_html=True)

# --- 2. 보안 및 환경 설정 ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    pw = st.text_input("접속 비밀번호를 입력하세요", type="password")
    if pw == "4321":
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.stop()

# GitHub 동기화를 위한 설정 (비워두면 로컬 모드로 작동)
GITHUB_TOKEN = st.sidebar.text_input("GitHub Token (선택사항)", type="password", help="자동 저장을 원하면 토큰을 입력하세요.")
REPO = "본인아이디/저장소이름" # 예: "kimyoong/qplay-archive"

# --- 3. 데이터 관리 로직 ---
DB_FILE = 'quizdata.json'

@st.cache_data
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

def save_data_locally():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state['data'], f, ensure_ascii=False, indent=2)

# --- 4. 검색 및 자동 복사 영역 ---
search_query = st.text_input("🔍 검색어 입력 (자동 복사: 첫 번째 결과)", placeholder="단어 사이는 공백으로 구분", key="search")

df = pd.DataFrame(st.session_state['data'])

if search_query and not df.empty:
    search_terms = search_query.split()
    filtered_df = df.copy()
    
    for term in search_terms:
        filtered_df = filtered_df[
            filtered_df['answer'].str.contains(term, case=False) | 
            filtered_df['keywords'].apply(lambda x: any(term.lower() in str(k).lower() for k in x))
        ]

    if not filtered_df.empty:
        # 정렬: 1순위 글자수, 2순위 가나다
        filtered_df['ans_len'] = filtered_df['answer'].str.len()
        filtered_df = filtered_df.sort_values(by=['ans_len', 'answer']).drop(columns=['ans_len'])

        # 최상단 정답 자동 복사 스크립트
        top_ans = filtered_df.iloc[0]['answer']
        st.components.v1.html(f"""
            <script>
            navigator.clipboard.writeText("{top_ans}");
            </script>
        """, height=0)
        
        st.success(f"📋 **'{top_ans}'** 복사 완료! (결과 {len(filtered_df)}건)")

        # 결과 리스트 출력
        for _, row in filtered_df.iterrows():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.code(row['answer'], language=None)
            with c2:
                kw_text = ", ".join(row['keywords'])
                for term in search_terms:
                    kw_text = kw_text.replace(term, f'<span class="highlight">{term}</span>')
                st.markdown(f"📍 {kw_text}", unsafe_allow_html=True)
    else:
        st.warning("결과가 없습니다.")

# --- 5. 데이터 관리 (추가/수정/삭제) ---
st.divider()
with st.expander("🛠️ 족보 관리자 모드"):
    tab1, tab2 = st.tabs(["문제 추가", "수정 및 삭제"])
    
    with tab1:
        with st.form("add"):
            a = st.text_input("정답")
            k = st.text_input("키워드 (쉼표로 구분)")
            if st.form_submit_button("추가"):
                new_item = {"answer": a, "keywords": [i.strip() for i in k.split(",") if i.strip()]}
                st.session_state['data'].append(new_item)
                save_data_locally()
                st.success("추가되었습니다!")
                st.rerun()

    with tab2:
        if st.session_state['data']:
            target = st.selectbox("수정할 문제 선택", [i['answer'] for i in st.session_state['data']])
            idx = next(i for i, v in enumerate(st.session_state['data']) if v['answer'] == target)
            
            with st.form("edit"):
                u_a = st.text_input("정답 수정", value=st.session_state['data'][idx]['answer'])
                u_k = st.text_input("키워드 수정", value=", ".join(st.session_state['data'][idx]['keywords']))
                col_b1, col_b2 = st.columns(2)
                if col_b1.form_submit_button("변경 저장"):
                    st.session_state['data'][idx] = {"answer": u_a, "keywords": [i.strip() for i in u_k.split(",")]}
                    save_data_locally()
                    st.rerun()
                if col_b2.form_submit_button("🔥 삭제"):
                    st.session_state['data'].pop(idx)
                    save_data_locally()
                    st.rerun()

# --- 6. 하단 이미지 배치 ---
st.write("---")
col_img1, col_img2 = st.columns(2)
with col_img1:
    if os.path.exists('logo.jpg'): st.image('logo.jpg', use_container_width=True)
with col_img2:
    if os.path.exists('deco.jpg'): st.image('deco.jpg', use_container_width=True)