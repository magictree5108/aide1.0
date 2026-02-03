"""
Aide 1.0 - 공무원 AI 보좌관 (전국 버전)
법제처 Open API 연동: 법령, 자치법규, 판례, 법령해석례, 행정심판례, 행정규칙
"""
import streamlit as st
import os
import requests
from openai import OpenAI

# ============================================
# 설정
# ============================================
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 법제처 API 기본 설정
LAW_API_BASE = "http://www.law.go.kr/DRF"
API_OC = "test"  # 실제 서비스 시 발급받은 OC로 변경

# ============================================

# 페이지 설정
st.set_page_config(
    page_title="Aide 1.0 - 공무원 AI 보좌관",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit 기본 요소 숨기기 + 모바일 대응
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    
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
    
    .main-header {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 50%, #4f46e5 100%);
        padding: 2rem 2.5rem;
        border-radius: 1.25rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px -10px rgba(30, 64, 175, 0.4);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.35rem 1rem;
        border-radius: 2rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.75rem;
        border: 1px solid rgba(255,255,255,0.3);
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
    
    .source-tag {
        display: block;
        padding: 0.5rem 0.8rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.4rem 0;
    }
    
    .source-tag a {
        text-decoration: none;
    }
    
    .source-tag a:hover {
        text-decoration: underline;
    }
    
    /* 소스 타입별 색상 */
    .source-law {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #93c5fd;
    }
    .source-law a { color: #1e40af; }
    
    .source-ordinance {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #34d399;
    }
    .source-ordinance a { color: #065f46; }
    
    .source-precedent {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
    }
    .source-precedent a { color: #92400e; }
    
    .source-interpretation {
        background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
        border: 1px solid #f472b6;
    }
    .source-interpretation a { color: #9d174d; }
    
    .source-adminjudge {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        border: 1px solid #a5b4fc;
    }
    .source-adminjudge a { color: #3730a3; }
    
    .source-adminrule {
        background: linear-gradient(135deg, #f5f5f4 0%, #e7e5e4 100%);
        border: 1px solid #a8a29e;
    }
    .source-adminrule a { color: #44403c; }
    
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
    }
    
    .guide-card {
        background: rgba(255,255,255,0.08);
        padding: 1rem 1.25rem;
        border-radius: 0.875rem;
        margin-bottom: 0.875rem;
        border: 1px solid rgba(255,255,255,0.1);
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
    
    .stTextArea textarea {
        border-radius: 1rem !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.875rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
    }
    
    .stSpinner > div > div { color: #0369a1 !important; }
    .stSpinner > div > span { color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)


# ============================================
# OpenAI 클라이언트
# ============================================
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = get_openai_client()


# ============================================
# 법제처 API 함수들
# ============================================

def search_law(query, num_results=3):
    """1. 법령 검색"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {
            "OC": API_OC,
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
            if law_id and law_name:
                detail = get_law_detail(law_id)
                if detail:
                    results.append({
                        "type": "법령",
                        "name": law_name,
                        "content": detail,
                        "url": f"https://www.law.go.kr/법령/{law_name}"
                    })
        return results
    except Exception as e:
        return []


def get_law_detail(law_id):
    """법령 본문 조회"""
    try:
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "law",
            "type": "JSON",
            "ID": law_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        articles = data.get("법령", {}).get("조문", {}).get("조문단위", [])
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
    except:
        return ""


def search_ordinance(query, local_gov="", num_results=3):
    """2. 자치법규 검색"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        search_query = f"{local_gov} {query}" if local_gov else query
        params = {
            "OC": API_OC,
            "target": "ordin",
            "type": "JSON",
            "query": search_query,
            "display": num_results
        }
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
            ordin_name = ordin.get("자치법규명한글", "") or ordin.get("법령명한글", "")
            local_name = ordin.get("자치단체명", "")
            ordin_id = ordin.get("자치법규ID", "") or ordin.get("법령ID", "")
            
            if ordin_name:
                detail = get_ordinance_detail(ordin_id)
                results.append({
                    "type": "자치법규",
                    "name": f"[{local_name}] {ordin_name}" if local_name else ordin_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/자치법규/{ordin_name}"
                })
        return results
    except:
        return []


def get_ordinance_detail(ordin_id):
    """자치법규 본문 조회"""
    try:
        if not ordin_id:
            return ""
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "ordin",
            "type": "JSON",
            "ID": ordin_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        law_info = data.get("자치법규", {}) or data.get("법령", {})
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
    except:
        return ""


def search_precedent(query, num_results=3):
    """3. 판례 검색"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "prec",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        precs = data.get("PrecSearch", {}).get("prec", [])
        if not precs:
            return []
        if isinstance(precs, dict):
            precs = [precs]
        
        results = []
        for prec in precs[:num_results]:
            prec_id = prec.get("판례일련번호", "")
            case_name = prec.get("사건명", "")
            case_num = prec.get("사건번호", "")
            court = prec.get("법원명", "")
            
            if prec_id:
                detail = get_precedent_detail(prec_id)
                results.append({
                    "type": "판례",
                    "name": f"[{court}] {case_name} ({case_num})",
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/판례/{case_num}"
                })
        return results
    except:
        return []


def get_precedent_detail(prec_id):
    """판례 본문 조회"""
    try:
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "prec",
            "type": "JSON",
            "ID": prec_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        prec_info = data.get("판례", {})
        
        content = ""
        if prec_info.get("판시사항"):
            content += f"[판시사항]\n{prec_info.get('판시사항')}\n\n"
        if prec_info.get("판결요지"):
            content += f"[판결요지]\n{prec_info.get('판결요지')}\n\n"
        if prec_info.get("참조조문"):
            content += f"[참조조문] {prec_info.get('참조조문')}\n\n"
        
        return content[:3000]
    except:
        return ""


def search_interpretation(query, num_results=3):
    """4. 법령해석례 검색"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "expc",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        expcs = data.get("ExpcSearch", {}).get("expc", [])
        if not expcs:
            return []
        if isinstance(expcs, dict):
            expcs = [expcs]
        
        results = []
        for expc in expcs[:num_results]:
            expc_id = expc.get("법령해석례일련번호", "")
            title = expc.get("안건명", "") or expc.get("제목", "")
            
            if expc_id:
                detail = get_interpretation_detail(expc_id)
                results.append({
                    "type": "법령해석례",
                    "name": title,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/법령해석례/{title}"
                })
        return results
    except:
        return []


def get_interpretation_detail(expc_id):
    """법령해석례 본문 조회"""
    try:
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "expc",
            "type": "JSON",
            "ID": expc_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        expc_info = data.get("법령해석례", {})
        
        content = ""
        if expc_info.get("질의요지"):
            content += f"[질의요지]\n{expc_info.get('질의요지')}\n\n"
        if expc_info.get("회답"):
            content += f"[회답]\n{expc_info.get('회답')}\n\n"
        if expc_info.get("이유"):
            content += f"[이유]\n{expc_info.get('이유')}\n\n"
        
        return content[:3000]
    except:
        return ""


def search_admin_judge(query, num_results=3):
    """5. 행정심판례 검색"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "detc",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        detcs = data.get("DetcSearch", {}).get("detc", [])
        if not detcs:
            return []
        if isinstance(detcs, dict):
            detcs = [detcs]
        
        results = []
        for detc in detcs[:num_results]:
            detc_id = detc.get("행정심판례일련번호", "")
            title = detc.get("사건명", "") or detc.get("제목", "")
            case_num = detc.get("사건번호", "")
            
            if title:
                detail = get_admin_judge_detail(detc_id) if detc_id else ""
                results.append({
                    "type": "행정심판례",
                    "name": f"{title} ({case_num})" if case_num else title,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/행정심판례/{case_num if case_num else title}"
                })
        return results
    except:
        return []


def get_admin_judge_detail(detc_id):
    """행정심판례 본문 조회"""
    try:
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "detc",
            "type": "JSON",
            "ID": detc_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        detc_info = data.get("행정심판례", {})
        
        content = ""
        if detc_info.get("재결요지"):
            content += f"[재결요지]\n{detc_info.get('재결요지')}\n\n"
        if detc_info.get("주문"):
            content += f"[주문]\n{detc_info.get('주문')}\n\n"
        
        return content[:3000]
    except:
        return ""


def search_admin_rule(query, num_results=3):
    """6. 행정규칙 검색 (훈령/예규/고시)"""
    try:
        url = f"{LAW_API_BASE}/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "admrul",
            "type": "JSON",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        rules = data.get("AdmrulSearch", {}).get("admrul", [])
        if not rules:
            return []
        if isinstance(rules, dict):
            rules = [rules]
        
        results = []
        for rule in rules[:num_results]:
            rule_id = rule.get("행정규칙일련번호", "")
            rule_name = rule.get("행정규칙명", "") or rule.get("제목", "")
            rule_type = rule.get("행정규칙종류", "")
            
            if rule_name:
                detail = get_admin_rule_detail(rule_id) if rule_id else ""
                results.append({
                    "type": "행정규칙",
                    "name": f"[{rule_type}] {rule_name}" if rule_type else rule_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/행정규칙/{rule_name}"
                })
        return results
    except:
        return []


def get_admin_rule_detail(rule_id):
    """행정규칙 본문 조회"""
    try:
        url = f"{LAW_API_BASE}/lawService.do"
        params = {
            "OC": API_OC,
            "target": "admrul",
            "type": "JSON",
            "ID": rule_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        data = response.json()
        rule_info = data.get("행정규칙", {})
        articles = rule_info.get("조문", {}).get("조문단위", [])
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
    except:
        return ""


# ============================================
# AI 응답 생성
# ============================================

SYSTEM_PROMPT = """당신은 대한민국 법령 전문가 AI 보좌관입니다.

## 사용 가능한 데이터
- 법령 (법률, 시행령, 시행규칙)
- 자치법규 (조례, 규칙)
- 판례 (대법원, 하급심)
- 법령해석례 (법제처 유권해석)
- 행정심판례
- 행정규칙 (훈령, 예규, 고시)

## 답변 원칙
1. **구체적 답변**: 검색된 내용을 직접 인용하여 설명
2. **근거 명시**: "OO법 제O조에 따르면...", "OO 판례에서는..." 형식
3. **실무 중심**: 공무원이 바로 활용할 수 있도록 답변
4. **종합 분석**: 법령 + 판례 + 해석례를 종합하여 답변

## 금지 사항
- "참조하세요", "확인하세요" 같은 떠넘기기 금지
- 검색 결과에 있으면 반드시 직접 설명
- 검색 결과에 없는 내용 지어내기 금지

## 답변 형식
1. 핵심 답변 (구체적 기준/요건/절차)
2. 관련 법령 근거
3. 판례/해석례 (있는 경우)
4. 실무 팁

## 마무리
항상 마지막에: "*AI 답변이므로 중요 사안은 원문을 반드시 확인하세요.*"
"""


def get_ai_response(messages, local_gov=""):
    user_query = messages[-1]['content']
    
    # 6개 API 병렬 검색
    law_results = search_law(user_query, num_results=2)
    ordinance_results = search_ordinance(user_query, local_gov=local_gov, num_results=2)
    precedent_results = search_precedent(user_query, num_results=2)
    interpretation_results = search_interpretation(user_query, num_results=2)
    admin_judge_results = search_admin_judge(user_query, num_results=2)
    admin_rule_results = search_admin_rule(user_query, num_results=2)
    
    # 컨텍스트 구성
    context = ""
    all_sources = []
    
    if law_results:
        context += "\n\n## 관련 법령:\n"
        for r in law_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if ordinance_results:
        context += "\n\n## 관련 자치법규:\n"
        for r in ordinance_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if precedent_results:
        context += "\n\n## 관련 판례:\n"
        for r in precedent_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if interpretation_results:
        context += "\n\n## 관련 법령해석례:\n"
        for r in interpretation_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if admin_judge_results:
        context += "\n\n## 관련 행정심판례:\n"
        for r in admin_judge_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if admin_rule_results:
        context += "\n\n## 관련 행정규칙:\n"
        for r in admin_rule_results:
            context += f"### {r['name']}\n{r['content']}\n"
            all_sources.append(r)
    
    if not context:
        context = "\n\n(관련 자료를 찾지 못했습니다.)\n"
    
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
# 세션 상태
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
        <div style="font-size: 1.5rem; font-weight: 700;">Aide 1.0</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">공무원 AI 법령 보좌관</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🏛️ 지자체 설정</div>', unsafe_allow_html=True)
    local_gov = st.text_input(
        "소속 지자체",
        value=st.session_state.local_gov,
        placeholder="예: 서울특별시 성동구",
        help="입력하면 해당 지자체 조례 우선 검색"
    )
    st.session_state.local_gov = local_gov
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 검색 범위</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-card">
        <div class="guide-card-text">
        📜 법령 (법률/시행령/시행규칙)<br>
        📋 자치법규 (조례/규칙)<br>
        ⚖️ 판례 (대법원/하급심)<br>
        💬 법령해석례 (유권해석)<br>
        📝 행정심판례<br>
        📁 행정규칙 (훈령/예규/고시)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ 예시 질문</div>', unsafe_allow_html=True)
    
    examples = [
        "건축허가 요건이 뭐야?",
        "개인정보 보유기간은?",
        "공무원 징계 종류 알려줘",
        "음식점 영업신고 절차는?",
    ]
    
    for q in examples:
        if st.button(f"→ {q}", key=f"ex_{q}", use_container_width=True):
            st.session_state.input_text = q
            st.rerun()


# ============================================
# 메인
# ============================================
st.markdown("""
<div class="main-header">
    <h1>⚖️ Aide 1.0 <span class="header-badge">공무원 AI 보좌관</span></h1>
    <p>법령 · 판례 · 해석례 · 행정규칙 통합 검색 | 법제처 Open API 연동</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-badge">
    <span>✅</span>
    <span>법제처 API 6종 연동 완료</span>
</div>
""", unsafe_allow_html=True)

# 채팅 영역
chat_html = '<div class="chat-container">'

if not st.session_state.messages:
    chat_html += """
    <div class="ai-message">
        <strong>안녕하세요! 공무원 AI 법령 보좌관입니다. ⚖️</strong><br><br>
        <strong>6가지 법령 데이터</strong>를 통합 검색합니다:<br>
        📜 법령 | 📋 자치법규 | ⚖️ 판례 | 💬 해석례 | 📝 심판례 | 📁 행정규칙<br><br>
        💡 왼쪽에서 소속 지자체를 설정하면 해당 조례를 우선 검색합니다.
    </div>
    """

for msg in st.session_state.messages:
    if msg['role'] == 'user':
        chat_html += f'<div class="user-message">{msg["content"]}</div>'
    else:
        sources_html = ""
        if 'sources' in msg and msg['sources']:
            sources_html = "<br><br><strong>📎 참조 자료:</strong><br>"
            for src in msg['sources']:
                type_class = {
                    "법령": "source-law",
                    "자치법규": "source-ordinance",
                    "판례": "source-precedent",
                    "법령해석례": "source-interpretation",
                    "행정심판례": "source-adminjudge",
                    "행정규칙": "source-adminrule"
                }.get(src['type'], "source-law")
                
                type_icon = {
                    "법령": "📜",
                    "자치법규": "📋",
                    "판례": "⚖️",
                    "법령해석례": "💬",
                    "행정심판례": "📝",
                    "행정규칙": "📁"
                }.get(src['type'], "📄")
                
                sources_html += f'<div class="source-tag {type_class}"><a href="{src["url"]}" target="_blank">{type_icon} {src["name"]}</a></div>'
        
        chat_html += f'<div class="ai-message">{msg["content"]}{sources_html}</div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# 입력
st.markdown("<br>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_area(
        "질문",
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
    
    with st.spinner("🔍 법령 · 판례 · 해석례 검색 중..."):
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
                'content': f"⚠️ 오류: {str(e)}",
                'sources': []
            })
    
    st.session_state.input_text = ""
    st.rerun()

st.markdown("""
<div class="footer-warning">
    ⚠️ AI 답변은 참고용이며, 중요한 결정 시 <strong>국가법령정보센터</strong>에서 원문을 확인하세요.
</div>
""", unsafe_allow_html=True)
