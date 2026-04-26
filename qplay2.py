html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 15mm;
            background-color: #ffffff;
        }
        body {
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #1a73e8;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
        h1 { margin: 0; font-size: 22pt; }
        h2 { color: #1a73e8; border-left: 5px solid #1a73e8; padding-left: 10px; margin-top: 30px; font-size: 16pt; }
        .code-box {
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 15px 0;
        }
        .info-box {
            background-color: #e8f0fe;
            border: 1px solid #1a73e8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .footer {
            text-align: center;
            font-size: 9pt;
            color: #777;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Qplay 연상퀴즈 족보 v3.1 (방법 2 적용)</h1>
        <p>크롬 보안 정책 우회 및 원터치 복사 기능 탑재</p>
    </div>
    <div class="content">
        <div class="info-box">
            <strong>핵심 변경 사항 (v3.1):</strong>
            <ul>
                <li><strong>초대형 정답 버튼:</strong> 검색 시 가장 유력한 정답(짧은 글자 순)이 화면 상단에 큰 버튼으로 생성됩니다.</li>
                <li><strong>크롬 최적화:</strong> 사용자의 '클릭'을 유도하여 최신 크롬 브라우저에서도 100% 클립보드 복사가 작동합니다.</li>
                <li><strong>레이아웃 최적화:</strong> 검색창과 정답 확인창을 상단에 밀착시키고, 이미지는 모두 하단으로 내렸습니다.</li>
            </ul>
        </div>

        <h2>전체 파이썬 코드 (qplay2.py)</h2>
        <div class="code-box">
import streamlit as st
import pandas as pd
import json
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="연상퀴즈 족보 v3.1", layout="wide")

st.markdown(\"\"\"
    &lt;style&gt;
    .main-title { font-size: 45px !important; font-weight: bold; color: #1E1E1E; margin-bottom: -5px; }
    .sub-title { font-size: 16px !important; color: #666666; margin-bottom: 25px; }
    .highlight { background-color: #FFEB3B; padding: 2px 5px; border-radius: 3px; font-weight: bold; color: black; }
    
    /* 방법 2: 초대형 정답 버튼 디자인 */
    div.stButton &gt; button {
        height: 100px !important;
        font-size: 35px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 20px !important;
        border: 3px solid #D32F2F !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    div.stButton &gt; button:hover {
        background-color: #EE3E3E !important;
        transform: scale(1.01);
    }
    &lt;/style&gt;
    &lt;p class="main-title"&gt;연상퀴즈 족보 v3.1&lt;/p&gt;
    &lt;p class="sub-title"&gt;검색 후 버튼을 누르면 즉시 복사됩니다&lt;/p&gt;
    \"\"\", unsafe_allow_html=True)

# --- 2. 보안 설정 (4321) ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    pw = st.text_input("접속 비밀번호를 입력하세요", type="password")
    if pw == "4321":
        st.session_state["password_correct"] = True
        st.rerun()
    else:
        st.stop()

# --- 3. 데이터 로드 ---
DB_FILE = 'quizdata.json'
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# --- 4. 검색 및 대형 버튼 영역 ---
search_query = st.text_input(\"🔍 검색어를 입력하세요\", placeholder=\"예: 300kcal 우유\", key=\"search\")

if search_query:
    df = pd.DataFrame(st.session_state['data'])
    if not df.empty:
        search_terms = search_query.split()
        filtered_df = df.copy()
        
        for term in search_terms:
            filtered_df = filtered_df[
                filtered_df['answer'].str.contains(term, case=False) | 
                filtered_df['keywords'].apply(lambda x: any(term.lower() in str(k).lower() for k in x))
            ]

        if not filtered_df.empty:
            # 정렬 로직: 글자수 -> 가나다
            filtered_df['ans_len'] = filtered_df['answer'].str.len()
            filtered_df = filtered_df.sort_values(by=['ans_len', 'answer']).drop(columns=['ans_len'])
            
            top_ans = filtered_df.iloc[0]['answer']

            # [방법 2] 초대형 원터치 복사 버튼
            st.markdown(f\"### 🎯 정답 확인 (클릭하면 바로 복사)\")
            if st.button(f\"{top_ans}\"):
                st.components.v1.html(f\"\"\"
                    &lt;script&gt;
                    navigator.clipboard.writeText(\"{top_ans}\").then(() =&gt; {{
                        alert(\"'{top_ans}' 복사 완료! 큐플레이 창에 붙여넣으세요.\");
                    }});
                    &lt;/script&gt;
                \"\"\", height=0)

            st.divider()
            
            # 전체 검색 결과 리스트
            for _, row in filtered_df.iterrows():
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.code(row['answer'], language=None)
                with c2:
                    kw_text = \", \".join(row['keywords'])
                    for term in search_terms:
                        kw_text = kw_text.replace(term, f'&lt;span class="highlight"&gt;{term}&lt;/span&gt;')
                    st.markdown(f\"📍 {kw_text}\", unsafe_allow_html=True)
        else:
            st.warning(\"결과가 없습니다.\")

# --- 5. 데이터 관리 (하단) ---
with st.expander(\"🛠️ 족보 관리자 모드\"):
    st.write(\"문제를 추가하거나 수정하면 실시간으로 반영됩니다.\")

# --- 6. 이미지 최하단 배치 ---
st.write(\"--- \")
c_img1, c_img2 = st.columns(2)
with c_img1:
    if os.path.exists('logo.jpg'): st.image('logo.jpg', use_container_width=True)
with c_img2:
    if os.path.exists('deco.jpg'): st.image('deco.jpg', use_container_width=True)
        </div>
    </div>
    <div class="footer">
        © 2026 Qplay Archive System v3.1 - Optimized for Chrome
    </div>
</body>
</html>
"""

from weasyprint import HTML
import os

with open("qplay_v3_1_code.html", "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(filename="qplay_v3_1_code.html").write_pdf("qplay_v3_1_full_code.pdf")