# 📚 Aide AI - 성동구 전용 (Streamlit 버전)

## 로컬 실행

```bash
# 1. 패키지 설치
pip3 install -r requirements.txt

# 2. document_index.json 파일 복사 (기존 인덱싱한 파일)
# aide_ai_simple 폴더에서 document_index.json을 이 폴더로 복사

# 3. 실행
streamlit run app.py
```

## Streamlit Cloud 배포 (무료)

1. GitHub에 이 폴더 업로드
2. https://share.streamlit.io 접속
3. GitHub 연결 → 레포 선택 → 배포 클릭
4. 끝!

## 파일 구조

```
aide_ai_streamlit/
├── app.py                 # 메인 앱
├── requirements.txt       # 패키지 목록
├── document_index.json    # 인덱싱된 문서 (복사 필요)
└── README.md
```

## 주의사항

- `document_index.json` 파일이 반드시 있어야 합니다
- OpenAI API 키가 코드에 포함되어 있습니다 (배포 시 환경변수로 변경 권장)
