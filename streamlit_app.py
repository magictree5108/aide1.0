"""
Aide 1.0 - 공무원 AI 보좌관
법제처 Open API (XML 방식)
"""
import streamlit as st
import os
import requests
import xml.etree.ElementTree as ET
from openai import OpenAI

# ============================================
# 설정
# ============================================
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

API_OC = "howon0411"

# 페이지 설정
st.set_page_config(
    page_title="Aide 1.0 - 공무원 AI 보좌관",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 기본 요소 숨기기
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
    html, body, [class*="st-"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 50%, #4f46e5 100%);
        padding: 2rem 2.5rem; border-radius: 1.25rem; margin-bottom: 2rem;
        color: white; box-shadow: 0 10px 40px -10px rgba(30, 64, 175, 0.4);
    }
    .main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
    .main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem; }
    .header-badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        padding: 0.35rem 1rem; border-radius: 2rem; font-size: 0.8rem;
        margin-left: 0.75rem; border: 1px solid rgba(255,255,255,0.3);
    }
    .chat-container {
        background: white; border-radius: 1.25rem; padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
        min-height: 400px; max-height: 500px; overflow-y: auto;
    }
    .user-message {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%);
        color: white; padding: 1rem 1.25rem;
        border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
        margin: 0.75rem 0 0.75rem 25%; font-size: 0.95rem; line-height: 1.6;
    }
    .ai-message {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #1e293b; padding: 1.25rem 1.5rem;
        border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
        margin: 0.75rem 25% 0.75rem 0; border: 1px solid #e2e8f0;
        font-size: 0.95rem; line-height: 1.7;
    }
    .source-tag { display: block; padding: 0.5rem 0.8rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 500; margin: 0.4rem 0; }
    .source-tag a { text-decoration: none; }
    .source-tag a:hover { text-decoration: underline; }
    .source-law { background: #dbeafe; border: 1px solid #93c5fd; }
    .source-law a { color: #1e40af; }
    .source-ordinance { background: #d1fae5; border: 1px solid #34d399; }
    .source-ordinance a { color: #065f46; }
    .source-precedent { background: #fef3c7; border: 1px solid #fbbf24; }
    .source-precedent a { color: #92400e; }
    .source-interpretation { background: #fce7f3; border: 1px solid #f472b6; }
    .source-interpretation a { color: #9d174d; }
    .source-adminjudge { background: #e0e7ff; border: 1px solid #a5b4fc; }
    .source-adminjudge a { color: #3730a3; }
    .source-adminrule { background: #f5f5f4; border: 1px solid #a8a29e; }
    .source-adminrule a { color: #44403c; }
    .status-badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534; padding: 0.6rem 1.25rem; border-radius: 2rem;
        font-size: 0.85rem; font-weight: 500; border: 1px solid #86efac; margin-bottom: 1.5rem;
    }
    .footer-warning {
        background: #fef3c7; border: 1px solid #fbbf24;
        padding: 1rem 1.5rem; border-radius: 0.875rem;
        text-align: center; font-size: 0.85rem; color: #92400e; margin-top: 1.5rem;
    }
    .guide-card {
        background: rgba(255,255,255,0.08); padding: 1rem 1.25rem;
        border-radius: 0.875rem; margin-bottom: 0.875rem; border: 1px solid rgba(255,255,255,0.1);
    }
    .guide-card-text { font-size: 0.8rem; opacity: 0.8; line-height: 1.5; }
    .section-title {
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.1em; color: rgba(255,255,255,0.5);
        margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .stTextArea textarea { border-radius: 1rem !important; border: 2px solid #e2e8f0 !important; padding: 1rem !important; }
    .stButton > button {
        background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%) !important;
        color: white !important; border: none !important;
        border-radius: 0.875rem !important; padding: 0.75rem 2rem !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# OpenAI
# ============================================
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = get_openai_client()


# ============================================
# XML 파싱 헬퍼
# ============================================
def get_text(element, tag):
    """XML 요소에서 텍스트 추출"""
    el = element.find(tag)
    return el.text.strip() if el is not None and el.text else ""


# ============================================
# 법제처 API 함수들 (XML 방식)
# ============================================

def search_law(query, num_results=3):
    """1. 법령 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "law",
            "type": "XML",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for law in root.findall(".//law"):
            law_mst = get_text(law, "법령일련번호")
            law_name = get_text(law, "법령명한글")
            law_id = get_text(law, "법령ID")
            
            if law_mst and law_name:
                detail = get_law_detail(law_mst)
                results.append({
                    "type": "법령",
                    "name": law_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/법령/{law_name}"
                })
        return results
    except Exception as e:
        return []


def get_law_detail(law_mst):
    """법령 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "law",
            "MST": law_mst,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        for article in root.findall(".//조문단위")[:15]:
            jo_num = get_text(article, "조문번호")
            jo_title = get_text(article, "조문제목")
            jo_content = get_text(article, "조문내용")
            
            if jo_content:
                title_str = f"({jo_title})" if jo_title else ""
                content += f"제{jo_num}조{title_str} {jo_content}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


def search_ordinance(query, local_gov="", num_results=3):
    """2. 자치법규 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        search_query = f"{local_gov} {query}" if local_gov else query
        params = {
            "OC": API_OC,
            "target": "ordin",
            "type": "XML",
            "query": search_query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for law in root.findall(".//law"):
            ordin_mst = get_text(law, "자치법규일련번호")
            ordin_name = get_text(law, "자치법규명")
            local_name = get_text(law, "지자체기관명")
            
            if ordin_mst and ordin_name:
                detail = get_ordinance_detail(ordin_mst)
                display_name = f"[{local_name}] {ordin_name}" if local_name else ordin_name
                results.append({
                    "type": "자치법규",
                    "name": display_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/자치법규/{ordin_name}"
                })
        return results
    except:
        return []


def get_ordinance_detail(ordin_mst):
    """자치법규 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "ordin",
            "MST": ordin_mst,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        for article in root.findall(".//조문단위")[:15]:
            jo_num = get_text(article, "조문번호")
            jo_title = get_text(article, "조문제목")
            jo_content = get_text(article, "조문내용")
            
            if jo_content:
                title_str = f"({jo_title})" if jo_title else ""
                content += f"제{jo_num}조{title_str} {jo_content}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


def search_precedent(query, num_results=3):
    """3. 판례 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "prec",
            "type": "XML",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for prec in root.findall(".//prec"):
            prec_id = get_text(prec, "판례일련번호")
            case_name = get_text(prec, "사건명")
            case_num = get_text(prec, "사건번호")
            court = get_text(prec, "법원명")
            
            if prec_id:
                detail = get_precedent_detail(prec_id)
                display_name = f"[{court}] {case_name} ({case_num})"
                results.append({
                    "type": "판례",
                    "name": display_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/판례/{case_num}"
                })
        return results
    except:
        return []


def get_precedent_detail(prec_id):
    """판례 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "prec",
            "ID": prec_id,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        판시사항 = get_text(root, ".//판시사항")
        판결요지 = get_text(root, ".//판결요지")
        참조조문 = get_text(root, ".//참조조문")
        
        if 판시사항:
            content += f"[판시사항]\n{판시사항}\n\n"
        if 판결요지:
            content += f"[판결요지]\n{판결요지}\n\n"
        if 참조조문:
            content += f"[참조조문] {참조조문}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


def search_interpretation(query, num_results=3):
    """4. 법령해석례 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "expc",
            "type": "XML",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for expc in root.findall(".//expc"):
            expc_id = get_text(expc, "법령해석례일련번호")
            title = get_text(expc, "안건명")
            
            if expc_id and title:
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
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "expc",
            "ID": expc_id,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        질의요지 = get_text(root, ".//질의요지")
        회답 = get_text(root, ".//회답")
        이유 = get_text(root, ".//이유")
        
        if 질의요지:
            content += f"[질의요지]\n{질의요지}\n\n"
        if 회답:
            content += f"[회답]\n{회답}\n\n"
        if 이유:
            content += f"[이유]\n{이유}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


def search_admin_judge(query, num_results=3):
    """5. 행정심판례 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "decc",
            "type": "XML",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for decc in root.findall(".//decc"):
            decc_id = get_text(decc, "행정심판례일련번호")
            title = get_text(decc, "사건명")
            case_num = get_text(decc, "사건번호")
            
            if decc_id and title:
                detail = get_admin_judge_detail(decc_id)
                display_name = f"{title} ({case_num})" if case_num else title
                results.append({
                    "type": "행정심판례",
                    "name": display_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/행정심판례/{case_num}"
                })
        return results
    except:
        return []


def get_admin_judge_detail(decc_id):
    """행정심판례 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "decc",
            "ID": decc_id,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        재결요지 = get_text(root, ".//재결요지")
        주문 = get_text(root, ".//주문")
        
        if 재결요지:
            content += f"[재결요지]\n{재결요지}\n\n"
        if 주문:
            content += f"[주문]\n{주문}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


def search_admin_rule(query, num_results=3):
    """6. 행정규칙 목록 검색"""
    try:
        url = "http://www.law.go.kr/DRF/lawSearch.do"
        params = {
            "OC": API_OC,
            "target": "admrul",
            "type": "XML",
            "query": query,
            "display": num_results
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        results = []
        
        for rule in root.findall(".//admrul"):
            rule_mst = get_text(rule, "행정규칙일련번호")
            rule_name = get_text(rule, "행정규칙명")
            rule_type = get_text(rule, "행정규칙종류")
            
            if rule_mst and rule_name:
                detail = get_admin_rule_detail(rule_mst)
                display_name = f"[{rule_type}] {rule_name}" if rule_type else rule_name
                results.append({
                    "type": "행정규칙",
                    "name": display_name,
                    "content": detail if detail else "(본문 조회 불가)",
                    "url": f"https://www.law.go.kr/행정규칙/{rule_name}"
                })
        return results
    except:
        return []


def get_admin_rule_detail(rule_mst):
    """행정규칙 본문 조회"""
    try:
        url = "http://www.law.go.kr/DRF/lawService.do"
        params = {
            "OC": API_OC,
            "target": "admrul",
            "MST": rule_mst,
            "type": "XML"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return ""
        
        root = ET.fromstring(response.content)
        content = ""
        
        for article in root.findall(".//조문단위")[:15]:
            jo_num = get_text(article, "조문번호")
            jo_title = get_text(article, "조문제목")
            jo_content = get_text(article, "조문내용")
            
            if jo_content:
                title_str = f"({jo_title})" if jo_title else ""
                content += f"제{jo_num}조{title_str} {jo_content}\n\n"
        
        return content[:4000] if content else ""
    except:
        return ""


# ============================================
# AI 응답
# ============================================

SYSTEM_PROMPT = """당신은 대한민국 법령 전문가 AI입니다.

## 역할
아래 [검색 결과]의 법령/시행령/시행규칙/판례/해석례 내용을 분석하여 사용자 질문에 답변합니다.

## 답변 방식
1. 법령명은 「」로 표시 (예: 「예비군법」, 「예비군법 시행령」)
2. 검색된 조문 내용을 바탕으로 질문에 맞게 정리
3. 법률뿐 아니라 시행령, 시행규칙 내용도 적극 활용
4. 사용자가 묻는 내용과 관련된 조문을 찾아서 설명
5. 검색 결과에 관련 내용이 있으면 종합적으로 답변

## 답변 형식
- 핵심 답변 먼저
- 「법령명」 제O조에 따르면... 형식으로 근거 제시
- 필요시 여러 법령/시행령 내용 종합

## 검색 결과가 정말 없을 때만
"검색 결과에서 관련 규정을 찾지 못했습니다."

## 마무리
"*검색된 법령 기준 답변이며, 정확한 내용은 원문 확인 필요*"
"""


def extract_search_keywords(user_query):
    """GPT로 검색 키워드 추출 - 핵심 단어 1~2개만"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """법령 검색용 핵심 키워드를 추출하세요.

규칙:
1. 가장 핵심적인 명사 1~2개만 (최대 2단어)
2. 길면 검색 안 됨. 짧게!
3. 지역명은 별도로 뒤에 추가

예시:
- "예비군 편성 의무기간 알려줘" → "예비군"
- "건축허가 요건이 뭐야?" → "건축허가"
- "개인정보 보유기간 규정" → "개인정보"
- "성동구 주차장 설치 기준" → "주차장, 성동구"
- "공무원 징계 종류 알려줘" → "공무원 징계"
- "음식점 영업신고 절차" → "영업신고"

키워드만 출력:"""},
                {"role": "user", "content": user_query}
            ],
            max_tokens=30,
            temperature=0
        )
        keywords = response.choices[0].message.content.strip()
        return keywords
    except:
        # 실패시 첫 2단어만
        words = user_query.split()[:2]
        return " ".join(words)


def get_ai_response(messages, local_gov=""):
    user_query = messages[-1]['content']
    
    # 1단계: 검색 키워드 추출
    keywords = extract_search_keywords(user_query)
    keyword_list = [k.strip() for k in keywords.split(",")]
    
    # 메인 키워드 (첫 번째)
    main_keyword = keyword_list[0] if keyword_list else user_query
    
    # 지역명 확인 (키워드에서 또는 local_gov에서)
    region = local_gov
    for kw in keyword_list:
        if any(loc in kw for loc in ["시", "구", "군", "도"]):
            region = kw
            break
    
    # 6개 API 검색 (추출된 키워드로)
    law_results = search_law(main_keyword, 2)
    ordinance_results = search_ordinance(main_keyword, region, 3)
    precedent_results = search_precedent(main_keyword, 2)
    interpretation_results = search_interpretation(main_keyword, 2)
    admin_judge_results = search_admin_judge(main_keyword, 2)
    admin_rule_results = search_admin_rule(main_keyword, 2)
    
    # 컨텍스트 구성
    context = "\n\n[검색 결과]"
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
    
    if not all_sources:
        context += "\n\n(검색 결과 없음)\n"
    else:
        # 디버깅용
        context += f"\n\n(총 {len(all_sources)}개 검색됨)\n"
    
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT + context},
    ] + messages
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        max_tokens=2048,
        temperature=0.3
    )
    
    return response.choices[0].message.content, all_sources


# ============================================
# 세션
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
        <div style="font-size: 2.5rem;">⚖️</div>
        <div style="font-size: 1.5rem; font-weight: 700;">Aide 1.0</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">공무원 AI 법령 보좌관</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🏛️ 지자체 설정</div>', unsafe_allow_html=True)
    local_gov = st.text_input(
        "소속 지자체",
        value=st.session_state.local_gov,
        placeholder="예: 서울특별시 성동구",
        help="입력시 해당 지자체 조례 우선 검색"
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
    
    for q in ["건축허가 요건은?", "개인정보 보유기간은?", "공무원 징계 종류는?", "음식점 영업신고 절차는?"]:
        if st.button(f"→ {q}", key=f"ex_{q}", use_container_width=True):
            st.session_state.input_text = q
            st.rerun()


# ============================================
# 메인
# ============================================
st.markdown("""
<div class="main-header">
    <h1>⚖️ Aide 1.0 <span class="header-badge">공무원 AI 보좌관</span></h1>
    <p>법령 · 판례 · 해석례 · 행정규칙 통합 검색 | 법제처 Open API</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="status-badge">✅ 법제처 API 6종 연동</div>', unsafe_allow_html=True)

# 채팅
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
                cls = {
                    "법령": "source-law", "자치법규": "source-ordinance",
                    "판례": "source-precedent", "법령해석례": "source-interpretation",
                    "행정심판례": "source-adminjudge", "행정규칙": "source-adminrule"
                }.get(src['type'], "source-law")
                icon = {
                    "법령": "📜", "자치법규": "📋", "판례": "⚖️",
                    "법령해석례": "💬", "행정심판례": "📝", "행정규칙": "📁"
                }.get(src['type'], "📄")
                sources_html += f'<div class="source-tag {cls}"><a href="{src["url"]}" target="_blank">{icon} {src["name"]}</a></div>'
        
        chat_html += f'<div class="ai-message">{msg["content"]}{sources_html}</div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# 입력
st.markdown("<br>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_area("질문", value=st.session_state.input_text, placeholder="법령에 대해 질문하세요...", height=80, label_visibility="collapsed")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    send_clicked = st.button("전송 →", use_container_width=True)

if send_clicked and user_input.strip():
    st.session_state.messages.append({'role': 'user', 'content': user_input.strip()})
    
    # 디버깅: 검색 키워드 표시
    keywords = extract_search_keywords(user_input.strip())
    st.info(f"🔍 검색 키워드: {keywords}")
    
    with st.spinner("🔍 법령 · 판례 · 해석례 검색 중..."):
        try:
            response, sources = get_ai_response(st.session_state.messages, st.session_state.local_gov)
            st.session_state.messages.append({'role': 'assistant', 'content': response, 'sources': sources})
        except Exception as e:
            st.session_state.messages.append({'role': 'assistant', 'content': f"⚠️ 오류: {str(e)}", 'sources': []})
    
    st.session_state.input_text = ""
    st.rerun()

st.markdown('<div class="footer-warning">⚠️ AI 답변은 참고용이며, 중요 결정시 <strong>국가법령정보센터</strong>에서 원문 확인 필요</div>', unsafe_allow_html=True)
