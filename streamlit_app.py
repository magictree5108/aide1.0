"""
Aide 1.0 - 공무원 AI 보좌관 (전국 버전)
"""
import streamlit as st
import json
import os
import requests
import numpy as np
from openai import OpenAI

# ============================================
# 설정
# ============================================
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ============================================

# 페이지 설정
st.set_page_config(
    page_title="Aide 1.0 beta - 공무원 AI 보좌관",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit 기본 요소 숨기기
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    
    /* 모바일에서 사이드바 숨김 */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {display: none !important;}
    }
</style>
""", unsafe_allow_html=True)

# 커스텀 CSS
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
        padding: 0.5rem 0.8rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.4rem 0;
        border: 1px solid #93c5fd;
    }
    
    .source-tag a {
        color: #1e40af;
        text-decoration: none;
    }
    
    .source-tag a:hover {
        text-decoration: underline;
    }
    
    .source-law {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        border: 1px solid #fbbf24;
    }
    
    .source-law a {
        color: #92400e;
    }
    
    .source-ordinance {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        border: 1px solid #34d399;
    }
    
    .source-ordinance a {
        color: #065f46;
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

client = get_openai_client()


# ============================================
# 국가법령정보센터 API 함수들
# ============================================

def search_law(query, num_results=5):
    """국가법령정보센터 API - 법령 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": "test",
            "target": "law",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        laws = data.get("LawSearch", {}).get("law", [])
        
        if not laws:
            return []
        
        if isinstance(laws, dict):
            laws = [laws]
        
        results = []
        for law in laws[:num_results]:
            law_id = law.get("법령ID", "")
            law_name = law.get("법령명한글", "")
            law_url = f"https://www.law.go.kr/법령/{law_name}"
            
            if law_id and law_name:
                # 법령 본문 조회
                detail = get_law_detail(law_id)
                if detail:
                    results.append({
                        "type": "법령",
                        "name": law_name,
                        "content": detail,
                        "url": law_url
                    })
        
        return results
    
    except Exception as e:
        print(f"법령 검색 오류: {e}")
        return []


def get_law_detail(law_id):
    """법령 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": "test",
            "target": "law",
            "type": "JSON",
            "ID": law_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        law_info = data.get("법령", {})
        
        # 조문 내용 추출
        articles = law_info.get("조문", {}).get("조문단위", [])
        if isinstance(articles, dict):
            articles = [articles]
        
        content = ""
        for art in articles[:10]:  # 처음 10개 조문
            jo_num = art.get("조문번호", "")
            jo_title = art.get("조문제목", "")
            jo_content = art.get("조문내용", "")
            if jo_content:
                content += f"제{jo_num}조({jo_title}) {jo_content}\n\n"
        
        return content[:3000]
    
    except Exception as e:
        print(f"법령 상세 조회 오류: {e}")
        return ""


def search_ordinance(query, local_gov="", num_results=5):
    """국가법령정보센터 API - 자치법규(조례) 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": "test",
            "target": "ordin",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        
        if local_gov:
            params["query"] = f"{local_gov} {query}"
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        ordins = data.get("LawSearch", {}).get("law", [])
        
        if not ordins:
            return []
        
        if isinstance(ordins, dict):
            ordins = [ordins]
        
        results = []
        for ordin in ordins[:num_results]:
            ordin_id = ordin.get("자치법규ID", "") or ordin.get("법령ID", "")
            ordin_name = ordin.get("자치법규명한글", "") or ordin.get("법령명한글", "")
            local_name = ordin.get("자치단체명", "") or ordin.get("지방자치단체명", "")
            ordin_url = f"https://www.law.go.kr/자치법규/{ordin_name}"
            
            if ordin_name:
                # 자치법규 본문 조회
                detail = get_ordinance_detail(ordin_id)
                results.append({
                    "type": "자치법규",
                    "name": f"[{local_name}] {ordin_name}" if local_name else ordin_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": ordin_url
                })
        
        return results
    
    except Exception as e:
        print(f"자치법규 검색 오류: {e}")
        return []


def get_ordinance_detail(ordin_id):
    """자치법규 본문 조회"""
    try:
        if not ordin_id:
            return ""
            
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": "test",
            "target": "ordin",
            "type": "JSON",
            "ID": ordin_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        law_info = data.get("자치법규", {}) or data.get("법령", {})
        
        # 조문 내용 추출
        articles = law_info.get("조문", {}).get("조문단위", [])
        if isinstance(articles, dict):
            articles = [articles]
        
        content = ""
        for art in articles[:10]:
            jo_num = art.get("조문번호", "")
            jo_title = art.get("조문제목", "")
            jo_content = art.get("조문내용", "")
            if jo_content:
                content += f"제{jo_num}조({jo_title}) {jo_content}\n\n"
        
        return content[:3000]
    
    except Exception as e:
        print(f"자치법규 상세 조회 오류: {e}")
        return ""


# ============================================
# AI 응답 생성
# ============================================

SYSTEM_PROMPT = """당신은 대한민국 법령 및 자치법규 전문가 AI 보좌관입니다.

## 핵심 원칙
1. **구체적 답변**: 검색된 법령/조례 내용을 직접 인용하여 답변
2. **조문 명시**: "OO법 제O조에 따르면..." 형식으로 근거 제시
3. **실무 중심**: 공무원이 바로 업무에 활용할 수 있도록 답변

## 답변 방식
1. 핵심 답변 먼저 (구체적 기준, 금액, 기간 등 포함)
2. 근거 조문 직접 인용
3. 실무 팁 또는 유의사항

## 금지 사항
- "참조하시기 바랍니다", "확인하세요" 같은 떠넘기기 금지
- 검색된 내용에 있으면 반드시 직접 설명
- 검색 결과에 없는 숫자/기준 지어내기 금지
- 없으면 "해당 내용은 검색 결과에 없습니다" 명시

## 답변 마무리
- 항상 마지막에: "*AI 답변이므로 중요 사안은 원문을 반드시 확인하세요.*"
"""


def get_ai_response(messages, local_gov=""):
    user_query = messages[-1]['content']
    
    # 1. 법령 검색
    law_results = search_law(user_query, num_results=3)
    
    # 2. 자치법규 검색
    ordinance_results = search_ordinance(user_query, local_gov=local_gov, num_results=3)
    
    # 컨텍스트 구성
    context = ""
    all_sources = []
    
    if law_results:
        context += "\n\n## 관련 법령:\n\n"
        for i, law in enumerate(law_results, 1):
            context += f"### [{law['name']}]\n{law['content']}\n\n"
            all_sources.append({
                "type": "법령",
                "name": law['name'],
                "url": law['url']
            })
    
    if ordinance_results:
        context += "\n\n## 관련 자치법규:\n\n"
        for i, ordin in enumerate(ordinance_results, 1):
            context += f"### [{ordin['name']}]\n{ordin['content']}\n\n"
            all_sources.append({
                "type": "자치법규",
                "name": ordin['name'],
                "url": ordin['url']
            })
    
    if not context:
        context = "\n\n(관련 법령 및 자치법규를 찾지 못했습니다.)\n"
    
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT + context},
    ] + messages
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        max_tokens=2048,
        temperature=0.7
    )
    
    return response.choices[0].message.content, all_sources


# ============================================
# 세션 상태 초기화
# ============================================
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'local_gov' not in st.session_state:
    st.session_state.local_gov = ""


# ============================================
# 사이드바
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚖️</div>
        <div style="font-size: 1.5rem; font-weight: 700;">Aide 1.0 beta</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">공무원 AI 법령 보좌관</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🏛️ 지자체 설정 (선택)</div>', unsafe_allow_html=True)
    
    local_gov = st.text_input(
        "소속 지자체",
        value=st.session_state.local_gov,
        placeholder="예: 서울특별시 성동구",
        help="입력하면 해당 지자체 조례 우선 검색"
    )
    st.session_state.local_gov = local_gov
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📖 이용 가이드</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">🔍</div>
        <div class="guide-card-title">실시간 법령 검색</div>
        <div class="guide-card-text">국가법령정보센터 API를 통해 최신 법령과 자치법규를 실시간 검색합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">📋</div>
        <div class="guide-card-title">출처 링크 제공</div>
        <div class="guide-card-text">모든 답변에 국가법령정보센터 링크가 포함됩니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-icon">🏛️</div>
        <div class="guide-card-title">지자체 설정</div>
        <div class="guide-card-text">소속 지자체를 입력하면 해당 자치법규를 우선 검색합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ 예시 질문</div>', unsafe_allow_html=True)
    
    example_questions = [
        "건축물 높이 제한 기준은?",
        "개인정보 보유기간 규정은?",
        "민원 처리 기한이 며칠이야?",
        "공무원 징계 종류 알려줘",
    ]
    
    for q in example_questions:
        if st.button(f"→ {q}", key=f"ex_{q}", use_container_width=True):
            st.session_state.input_text = q
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="contact-card">
        <div class="contact-card-title">📞 피드백 환영!</div>
        <div class="contact-card-text">개발자: 010-8829-5108</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# 메인 영역
# ============================================

# 헤더
st.markdown("""
<div class="main-header">
    <h1>⚖️ Aide 1.0 beta <span class="header-badge">공무원 AI 보좌관</span></h1>
    <p>국가법령정보센터 API 기반 실시간 법령 검색 · 근거 중심 답변 · 출처 링크 제공</p>
</div>
""", unsafe_allow_html=True)

# 메인 레이아웃
col_main = st.container()

with col_main:
    # 상태 표시
    st.markdown(f"""
    <div class="status-badge">
        <span>✅</span>
        <span>국가법령정보센터 API 연동 완료 · 전국 법령 및 자치법규 실시간 검색</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 채팅 영역
    chat_html = '<div class="chat-container">'
    
    if not st.session_state.messages:
        chat_html += """
        <div class="ai-message">
            <strong>안녕하세요! 공무원 AI 법령 보좌관입니다. ⚖️</strong><br><br>
            <strong>국가법령정보센터 API</strong>를 통해 전국의 법령과 자치법규를 실시간 검색합니다.<br>
            업무 관련 법령 질문을 편하게 해주세요!<br><br>
            💡 <strong>팁:</strong> 왼쪽에서 소속 지자체를 설정하면 해당 지역 조례를 우선 검색합니다.
        </div>
        """
    
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            chat_html += f'<div class="user-message">{msg["content"]}</div>'
        else:
            # 출처 표시
            sources_html = ""
            if 'sources' in msg and msg['sources']:
                sources_html = "<br><br><strong>📎 참조 법령:</strong><br>"
                for src in msg['sources']:
                    if src['type'] == '법령':
                        sources_html += f'<div class="source-tag source-law"><a href="{src["url"]}" target="_blank">📜 {src["name"]}</a></div>'
                    else:
                        sources_html += f'<div class="source-tag source-ordinance"><a href="{src["url"]}" target="_blank">📋 {src["name"]}</a></div>'
            
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
            placeholder="법령에 대해 질문하세요...",
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
        
        with st.spinner("🔍 법령 검색 및 답변 생성 중..."):
            try:
                response, sources = get_ai_response(
                    st.session_state.messages, 
                    local_gov=st.session_state.local_gov
                )
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'sources': sources
                })
            except Exception as e:
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"⚠️ 오류가 발생했습니다: {str(e)}",
                    'sources': []
                })
        
        st.session_state.input_text = ""
        st.rerun()
    
    # 면책 문구
    st.markdown("""
    <div class="footer-warning">
        ⚠️ Aide는 국가법령정보센터 API를 통해 법령을 검색하지만, AI 답변은 실수가 있을 수 있습니다.<br>
        중요한 결정 시 <strong>국가법령정보센터</strong>에서 원문을 반드시 확인하세요.
    </div>
    """, unsafe_allow_html=True)
