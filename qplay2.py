import streamlit as st
import pandas as pd
import json
import os
from streamlit_extras.stylable_container import stylable_container

# 1. 페이지 설정
st.set_page_config(page_title="Qplay 연상퀴즈 족보 v2.2", layout="wide")

# CSS: 검색어 하이라이트 및 레이아웃 조정
st.markdown("""
    <style>
    .main-title { font-size: 45px !important; font-weight: bold; color: #1E1E1E; margin-bottom: -10px; }
    .sub-title { font-size: 16px !important; color: #666666; margin-bottom: 20px; }
    .highlight { background-color: #FFEB3B; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .copy-msg { font-size: 12px; color: #28a745; font-weight: bold; }
    </style>
    <p class="main-title">연상퀴즈 족보 v2.2</p>
    <p class="sub-title">제시어로 정답을 빠르게 찾는 아카이브</p>
    """, unsafe_allow_html=True)

# 2. 비밀번호 보안 (4321)
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    pw = st.text_input("접속 비밀번호를 입력하세요", type="password")
    if pw == "4321":
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.stop()

# --- 비밀번호 통과 후 ---

# 데이터 로드
DB_FILE = 'quizdata.json'
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

data = load_data()
df = pd.DataFrame(data)

# 3. 검색창 (정답창과 밀착)
search_query = st.text_input("🔍 검색어 입력 (자동 복사: 결과의 첫 번째 정답)", placeholder="예: 300kcal", key="search_input")

if search_query:
    search_terms = search_query.split()
    filtered_df = df.copy()
    
    for term in search_terms:
        filtered_df = filtered_df[
            filtered_df['answer'].str.contains(term, case=False) | 
            filtered_df['keywords'].apply(lambda x: any(term.lower() in str(k).lower() for k in x))
        ]

    # 4. 정렬 로직 (1순위: 글자수 적은순, 2순위: 가나다순)
    if not filtered_df.empty:
        filtered_df['ans_len'] = filtered_df['answer'].str.len()
        filtered_df = filtered_df.sort_values(by=['ans_len', 'answer']).drop(columns=['ans_len'])

        # 자동 복사 기능 (첫 번째 결과물)
        top_answer = filtered_df.iloc[0]['answer']
        
        # 클립보드 복사를 위한 자바스크립트 삽입
        st.components.v1.html(f"""
            <script>
            const text = "{top_answer}";
            navigator.clipboard.writeText(text).then(() => {{
                parent.postMessage("copied", "*");
            }});
            </script>
        """, height=0)
        
        st.success(f"✅ 최상단 정답 **'{top_answer}'** 가 자동으로 복사되었습니다! (Ctrl+V 하세요)")

        # 결과 출력
        for _, row in filtered_df.iterrows():
            col_ans, col_key = st.columns([1, 4])
            with col_ans:
                st.code(row['answer'], language=None)
            with col_key:
                kv_text = ", ".join(row['keywords'])
                for term in search_terms:
                    kv_text = kv_text.replace(term, f'<span class="highlight">{term}</span>')
                st.markdown(f"📍 {kv_text}", unsafe_allow_html=True)
    else:
        st.warning("검색 결과가 없습니다.")

# 5. 그림 2개 (가장 아래로 이동 및 크기 통일)
st.write("---")
img_col1, img_col2 = st.columns(2)
with img_col1:
    if os.path.exists('logo.jpg'):
        st.image('logo.jpg', use_container_width=True)
with img_col2:
    if os.path.exists('deco.jpg'):
        st.image('deco.jpg', use_container_width=True)

# 6. 데이터 관리 (최하단 배치)
with st.expander("🛠️ 데이터 추가"):
    # (추가 기능 생략 - 이전과 동일)
    pass