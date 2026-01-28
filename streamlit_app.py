"""
Aide AI - 성동구 전용 (Streamlit 버전)
"""

import streamlit as st
import json
import os
import numpy as np
from openai import OpenAI

# ============================================
# 설정
# ============================================
OPENAI_API_KEY = "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"
INDEX_FILE = "./document_index.json"
# ============================================

# 페이지 설정
st.set_page_config(
    page_title="Aide AI - 성동구 전용",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.25rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    .badge {
        background: rgba(255,255,255,0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        margin-left: 0.5rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        margin-left: 20%;
    }
    
    .ai-message {
        background: #f1f5f9;
        color: #1e293b;
        margin-right: 20%;
    }
    
    .source-tag {
        background: #e0f2fe;
        color: #0369a1;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        margin-right: 0.25rem;
        display: inline-block;
        margin-top: 0.25rem;
    }
    
    .guide-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #0ea5e9;
    }
    
    .example-btn {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-btn:hover {
        background: #f0f9ff;
        border-color: #0ea5e9;
    }
    
    .footer-warning {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-size: 0.85rem;
        color: #92400e;
        margin-top: 1rem;
    }
    
    .doc-item {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.25rem;
        cursor: pointer;
        font-size: 0.85rem;
        transition: background 0.2s;
    }
    
    .doc-item:hover {
        background: #e0f2fe;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%);
    }
</style>
""", unsafe_allow_html=True)

# OpenAI 클라이언트
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

# 문서 인덱스 로드
@st.cache_data
def load_documents():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('documents', []), data.get('embeddings', [])
    return [], []

documents, embeddings = load_documents()
client = get_openai_client()


def get_embedding(text):
    """OpenAI 임베딩 생성"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000]
    )
    return response.data[0].embedding


def cosine_similarity(a, b):
    """코사인 유사도 계산"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_documents(query, n_results=5):
    """문서 검색"""
    if not documents or not embeddings:
        return []
    
    query_embedding = get_embedding(query)
    
    scores = []
    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_embedding, emb)
        scores.append((i, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = scores[:n_results]
    
    results = []
    for idx, score in top_indices:
        results.append({
            'content': documents[idx]['content'],
            'filename': documents[idx]['filename'],
            'score': float(score)
        })
    
    return results


SYSTEM_PROMPT = """당신은 성동구 조례를 기반으로 답변하는 AI 보좌관입니다.

## 역할
- 성동구의 조례, 규칙, 서식 등을 기반으로 정확한 정보를 제공합니다.
- 검색된 문서 내용을 바탕으로 답변합니다.
- 문서에 없는 내용은 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답합니다.

## 답변 원칙
1. **문서 기반**: 검색된 문서 내용을 근거로 답변
2. **출처 명시**: 어떤 문서에서 정보를 가져왔는지 표시
3. **정확성**: 문서에 없는 내용은 추측하지 않음
4. **친절함**: 공무원이 이해하기 쉽게 설명"""


def get_ai_response(messages):
    """AI 응답 생성"""
    user_query = messages[-1]['content']
    
    # 관련 문서 검색
    relevant_docs = search_documents(user_query, n_results=5)
    
    # 컨텍스트 구성
    context = ""
    if relevant_docs:
        context = "\n\n## 검색된 관련 문서:\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            context += f"### [문서 {i}] {doc['filename']}\n"
            context += f"{doc['content'][:2000]}\n\n"
    else:
        context = "\n\n(관련 문서를 찾지 못했습니다.)\n"
    
    # GPT-4에 질문
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


# 헤더
st.markdown("""
<div class="main-header">
    <h1>📚 Aide AI <span class="badge">성동구 전용</span></h1>
    <p>조례 기반 AI 업무 보좌관</p>
</div>
""", unsafe_allow_html=True)

# 3열 레이아웃
col1, col2, col3 = st.columns([1, 2, 1])

# 왼쪽 사이드바: 이용 가이드
with col1:
    st.markdown("### 📖 이용 가이드")
    
    st.markdown("""
    <div class="guide-card">
        <strong>💡 이렇게 질문하세요</strong><br>
        <small>구체적인 조례명이나 키워드로 질문하면 더 정확한 답변을 받을 수 있습니다.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <strong>📋 출처 확인</strong><br>
        <small>모든 답변에는 참조한 문서가 표시됩니다.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ 예시 질문")
    
    example_questions = [
        "자원봉사자 간병비 지원 신청 방법은?",
        "장기요양기관 지정 심사 기준이 뭐야?",
        "세무조사 범위 확대 통지 절차는?",
        "공유오피스 이용료가 얼마야?",
    ]
    
    for q in example_questions:
        if st.button(q, key=f"ex_{q}", use_container_width=True):
            st.session_state.input_text = q
            st.rerun()
    
    st.markdown("---")
    st.info("📞 **도움이 필요하신가요?**\n\n시스템 문의: 010-8829-5108")

# 메인 채팅 영역
with col2:
    # 상태 표시
    if documents:
        st.success(f"✅ 준비 완료! {len(documents)}개 문서 청크 학습됨")
    else:
        st.error("⚠️ 문서가 없습니다. index_documents.py를 먼저 실행하세요.")
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        # 환영 메시지
        if not st.session_state.messages:
            st.markdown("""
            <div class="ai-message chat-message">
                <strong>안녕하세요! 성동구 조례 AI 보좌관입니다. 👋</strong><br><br>
                성동구의 <strong>조례, 규칙, 서식</strong> 등을 학습했습니다.<br>
                업무 관련 질문을 편하게 해주세요!
            </div>
            """, unsafe_allow_html=True)
        
        # 메시지 표시
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="user-message chat-message">
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                sources_html = ""
                if 'sources' in msg and msg['sources']:
                    sources_html = "<br><br><small>📎 참조 문서: "
                    for s in msg['sources'][:3]:
                        sources_html += f'<span class="source-tag">{s[:30]}...</span>'
                    sources_html += "</small>"
                
                st.markdown(f"""
                <div class="ai-message chat-message">
                    {msg['content']}{sources_html}
                </div>
                """, unsafe_allow_html=True)
    
    # 입력 영역
    st.markdown("---")
    
    input_col1, input_col2 = st.columns([5, 1])
    
    with input_col1:
        user_input = st.text_area(
            "질문 입력",
            value=st.session_state.input_text,
            placeholder="조례에 대해 질문하세요...",
            height=80,
            label_visibility="collapsed"
        )
    
    with input_col2:
        send_clicked = st.button("전송", use_container_width=True, type="primary")
    
    if send_clicked and user_input.strip():
        # 사용자 메시지 추가
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input.strip()
        })
        
        # AI 응답 생성
        with st.spinner("조례 검색 및 답변 생성 중..."):
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
        ⚠️ Aide AI는 성동구 조례를 바탕으로 신뢰성 있는 답변을 제공하지만 실수를 할 수 있습니다. 중요한 결정 시 원문을 반드시 확인하세요.
    </div>
    """, unsafe_allow_html=True)

# 오른쪽: 문서 목록
with col3:
    st.markdown("### 📂 학습된 문서")
    
    # 검색
    search_query = st.text_input("문서 검색", placeholder="검색어 입력...", label_visibility="collapsed")
    
    # 문서 목록
    doc_names = list(set([doc['filename'] for doc in documents]))
    
    if search_query:
        doc_names = [d for d in doc_names if search_query.lower() in d.lower()]
    
    st.caption(f"총 {len(doc_names)}개 문서")
    
    doc_container = st.container()
    with doc_container:
        for doc_name in doc_names[:20]:  # 최대 20개 표시
            clean_name = doc_name.replace('.hwpx', '').replace('[', '').replace(']', '')
            if st.button(f"📄 {clean_name[:25]}...", key=f"doc_{doc_name}", use_container_width=True):
                st.session_state.input_text = f'"{clean_name}"에 대해 자세히 설명해줘'
                st.rerun()
