"""
Aide 1.0 - 성동구 전용 (Streamlit 버전)
"""
import streamlit as st
import json
import os
import glob
import numpy as np
from openai import OpenAI

# ============================================
# 설정
# ============================================
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

INDEX_FILE = "./document_index.json"
# ============================================

# 페이지 설정
st.set_page_config(
    page_title="Aide 1.0 beta - 성동구 전용",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit 기본 요소 숨기기
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stSidebarCollapseButton"] {display: none;}
</style>
""", unsafe_allow_html=True)

# 커스텀 CSS - 세련된 디자인
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1);
    }
    
    .main-header {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 50%, #4f46e5 100%);
        padding: 2rem 2.5rem;
        border-radius: 1.25rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px -10px rgba(30, 64, 175, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        position: relative;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
        position: relative;
    }
    
    .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: 0.35rem 1rem;
        border-radius: 2rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.75rem;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .guide-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        border-radius: 0.875rem;
        margin-bottom: 0.875rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .guide-card:hover {
        background: rgba(255,255,255,0.12);
        transform: translateX(4px);
    }
    
    .guide-card-icon {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
    
    .guide-card-title {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.35rem;
        color: #38bdf8 !important;
    }
    
    .guide-card-text {
        font-size: 0.8rem;
        opacity: 0.8;
        line-height: 1.5;
    }
    
    .chat-container {
        background: white;
        border-radius: 1.25rem;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
        margin: 0.75rem 0 0.75rem 25%;
        box-shadow: 0 4px 15px rgba(3, 105, 161, 0.25);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #1e293b;
        padding: 1.25rem 1.5rem;
        border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
        margin: 0.75rem 25% 0.75rem 0;
        border: 1px solid #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    .ai-message strong {
        color: #0369a1;
    }
    
    .source-tag {
        display: block;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.3rem 0;
        border: 1px solid #93c5fd;
    }
    
    .example-btn {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.15);
        color: white;
        padding: 0.7rem 1rem;
        border-radius: 0.75rem;
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .example-btn:hover {
        background: rgba(56, 189, 248, 0.2);
        border-color: #38bdf8;
        transform: translateX(4px);
    }
    
    .doc-item {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        color: #475569;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .doc-item:hover {
        background: #f0f9ff;
        border-color: #0ea5e9;
        color: #0369a1;
        transform: translateX(4px);
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 0.6rem 1.25rem;
        border-radius: 2rem;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #86efac;
        margin-bottom: 1.5rem;
    }
    
    .status-badge-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border-color: #fca5a5;
    }
    
    .footer-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
        padding: 1rem 1.5rem;
        border-radius: 0.875rem;
        text-align: center;
        font-size: 0.85rem;
        color: #92400e;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.15);
    }
    
    .contact-card {
        background: linear-gradient(135deg, rgba(56,189,248,0.15) 0%, rgba(14,165,233,0.1) 100%);
        border: 1px solid rgba(56,189,248,0.3);
        padding: 1rem 1.25rem;
        border-radius: 0.875rem;
        margin-top: 1rem;
    }
    
    .contact-card-title {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.35rem;
        color: #38bdf8 !important;
    }
    
    .contact-card-text {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    .stTextArea textarea {
        border-radius: 1rem !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.875rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 15px rgba(3, 105, 161, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(3, 105, 161, 0.4) !important;
    }

    .stSpinner > div > div {
        color: #0369a1 !important;
    }
    
    .stSpinner > div > span {
        color: #1e293b !important;
    }
    
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #94a3b8;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.5);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# OpenAI 클라이언트
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 문서 인덱스 로드 (여러 인덱스 파일 지원)
@st.cache_data
def load_documents():
    all_docs = []
    all_embeddings = []
    
    # 1. 기존 조례 인덱스 (document_index_part_*)
    doc_parts = sorted(glob.glob("document_index_part_*"))
    if doc_parts:
        combined = b""
        for pf in doc_parts:
            with open(pf, 'rb') as f:
                combined += f.read()
        data = json.loads(combined.decode('utf-8'))
        all_docs.extend(data.get('documents', []))
        all_embeddings.extend(data.get('embeddings', []))
    
    # 2. 웹 크롤링 인덱스 (web_index_part_*)
    web_parts = sorted(glob.glob("web_index_part_*"))
    if web_parts:
        combined = b""
        for pf in web_parts:
            with open(pf, 'rb') as f:
                combined += f.read()
        data = json.loads(combined.decode('utf-8'))
        all_docs.extend(data.get('documents', []))
        all_embeddings.extend(data.get('embeddings', []))
    
    # 3. 추가 인덱스 (extra_index_part_*) - 미래 확장용
    extra_parts = sorted(glob.glob("extra_index_part_*"))
    if extra_parts:
        combined = b""
        for pf in extra_parts:
            with open(pf, 'rb') as f:
                combined += f.read()
        data = json.loads(combined.decode('utf-8'))
        all_docs.extend(data.get('documents', []))
        all_embeddings.extend(data.get('embeddings', []))
    
    # 4. 단일 파일 폴백 (로컬 테스트용)
    if not all_docs:
        for index_file in ["document_index.json", "web_index.json", "extra_index.json"]:
            if os.path.exists(index_file):
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_docs.extend(data.get('documents', []))
                    all_embeddings.extend(data.get('embeddings', []))
    
    return all_docs, all_embeddings

documents, embeddings = load_documents()
client = get_openai_client()


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000]
    )
    return response.data[0].embedding


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_documents(query, n_results=10):
    if not documents or not embeddings:
        return []
    
    # 1. 벡터 검색 (의미 기반)
    query_embedding = get_embedding(query)
    vector_scores = []
    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_embedding, emb)
        vector_scores.append((i, score))
    
    # 2. 키워드 검색 (단어 매칭)
    query_keywords = set(query.lower().replace('?', '').replace('.', '').split())
    keyword_scores = []
    for i, doc in enumerate(documents):
        content = doc['content'].lower() + doc['filename'].lower()
        matches = sum(1 for kw in query_keywords if kw in content)
        keyword_scores.append((i, matches / max(len(query_keywords), 1)))
    
    # 3. 점수 합산 (벡터 70% + 키워드 30%)
    combined_scores = []
    for i in range(len(documents)):
        v_score = vector_scores[i][1]
        k_score = keyword_scores[i][1]
        combined = (v_score * 0.7) + (k_score * 0.3)
        combined_scores.append((i, combined))
    
    # 4. 정렬 및 상위 결과 반환
    combined_scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = combined_scores[:n_results]
    
    results = []
    for idx, score in top_indices:
        results.append({
            'content': documents[idx]['content'],
            'filename': documents[idx]['filename'],
            'score': float(score)
        })
    
    return results


SYSTEM_PROMPT = """당신은 성동구 조례 전문가 AI 보좌관입니다.
## 핵심 원칙
1. **추론**: 질문 의도를 파악해 관련 조례를 능동적으로 연결
2. **근거 기반**: 답변 시 반드시 조례명, 조항 명시
3. **유연한 탐색**: 직접적인 조례가 없으면 유사/상위 개념 조례 활용
4. **상위법 안내**: 구 조례에 없으면 해당 상위법 안내
## 답변 방식
- 핵심 답변 먼저 → 근거 조항 → 실무 팁
- 없는 경우: "성동구 조례에 직접 규정 없음. [관련 조례] 유추 적용 가능" 또는 "[상위법] 적용 필요"
- 근거 없이 숫자(과태료, 기간 등) 지어내지 않음
- 불확실하면 "확인 필요" 명시
## 답변 마무리
- 모든 답변 끝에 다음 문구 추가: "*별표, 서식 관련 내용은 오류가 날 수 있습니다*"
"""


def get_ai_response(messages):
    user_query = messages[-1]['content']
    relevant_docs = search_documents(user_query, n_results=5)
    
    context = ""
    if relevant_docs:
        context = "\n\n## 검색된 관련 문서:\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            context += f"### [문서 {i}] {doc['filename']}\n"
            context += f"{doc['content'][:2000]}\n\n"
    else:
        context = "\n\n(관련 문서를 찾지 못했습니다.)\n"
    
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT + context},
    ] + messages
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        max_tokens=2048,
        temperature=0.7
    )
    
    return response.choices[0].message.content, [doc['filename'] for doc in relevant_docs]


# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""


# ============================================
# 사이드바
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏛️</div>
        <div style="font-size: 1.5rem; font-weight: 700;">Aide 1.0 beta</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">신뢰할 수 있는 공공업무 특화 Chat bot</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📖 이용 가이드</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">💡</div>
        <div class="guide-card-title">이렇게 질문하세요</div>
        <div class="guide-card-text">구체적인 조례명이나 키워드로 질문하면 더 정확한 답변을 받을 수 있습니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">📋</div>
        <div class="guide-card-title">출처 확인</div>
        <div class="guide-card-text">모든 답변에는 참조한 문서가 표시됩니다. 원문 확인이 필요하면 해당 조례를 찾아보세요.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">🔄</div>
        <div class="guide-card-title">대화 이어가기</div>
        <div class="guide-card-text">추가 질문이나 관련 내용을 이어서 물어볼 수 있습니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ 예시 질문</div>', unsafe_allow_html=True)
    
    example_questions = [
        "자원봉사자 간병비 지원 신청 방법은?",
        "장기요양기관 지정 심사 기준이 뭐야?",
        "세무조사 범위 확대 통지 절차는?",
        "공유오피스 이용료가 얼마야?",
    ]
    
    for q in example_questions:
        if st.button(f"→ {q}", key=f"ex_{q}", use_container_width=True):
            st.session_state.input_text = q
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="contact-card">
        <div class="contact-card-title">📞문의사항이 있으신가요?</div>
        <div class="contact-card-text">개발자(정호원): 010-8829-5108</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# 메인 영역
# ============================================

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🏛️ Aide 1.0 beta <span class="header-badge">성동구 전용</span></h1>
    <p>자치법규 기반 AI 업무 보좌관 · 철저한 근거를 기반합니다. 거짓말 없이 모르면 모른다고 합니다.</p>
</div>
""", unsafe_allow_html=True)

# 메인 레이아웃
col_main = st.container()

with col_main:
    # 상태 표시
    if documents:
        st.markdown(f"""
        <div class="status-badge">
            <span>✅</span>
            <span>준비 완료! {len(documents)}개 자치법규 및 공문서 학습됨</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge status-badge-error">
            <span>⚠️</span>
            <span>문서가 없습니다. index_documents.py를 먼저 실행하세요.</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 채팅 영역
    chat_html = '<div class="chat-container">'
    
    if not st.session_state.messages:
        chat_html += """
        <div class="ai-message">
            <strong>안녕하세요! 성동구 조례 AI 보좌관입니다. 👋</strong><br><br>
            성동구의 <strong>조례, 규칙, 서식</strong> 등을 학습했습니다.<br>
            업무 관련 질문을 편하게 해주세요!
        </div>
        """
    
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            chat_html += f'<div class="user-message">{msg["content"]}</div>'
        else:
            sources_html = ""
            if 'sources' in msg and msg['sources']:
                sources_html = "<br><br><small>📎 참조 문서:</small><br>"
                for s in list(set(msg['sources']))[:5]:
                    full_name = s.replace('.hwpx', '').replace('.pdf', '')
                    sources_html += f'<div class="source-tag">{full_name}</div>'
            chat_html += f'<div class="ai-message">{msg["content"]}{sources_html}</div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # 입력 영역
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_area(
            "질문 입력",
            value=st.session_state.input_text,
            placeholder="조례에 대해 질문하세요...",
            height=80,
            label_visibility="collapsed"
        )
    
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        send_clicked = st.button("전송 →", use_container_width=True)
    
    if send_clicked and user_input.strip():
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input.strip()
        })
        
        with st.spinner("🔍 조례 검색 및 답변 생성 중..."):
            try:
                response, sources = get_ai_response(st.session_state.messages)
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'sources': sources
                })
            except Exception as e:
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"⚠️ 오류가 발생했습니다: {str(e)}"
                })
        
        st.session_state.input_text = ""
        st.rerun()
    
    # 면책 문구
    st.markdown("""
    <div class="footer-warning">
        ⚠️ Aide 1.0 beta는 성동구 조례를 바탕으로 신뢰성 있는 답변을 제공하지만 실수를 할 수 있습니다.<br>
        중요한 결정 시 원문을 반드시 확인하세요.
    </div>
    """, unsafe_allow_html=True)
