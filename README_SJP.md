# README_SJP - 교육생용 빠른 시작 안내

**과제 제출자 : 신 재 풍**

## 무엇을 만든 프로그램인가요?

여행 날짜와 스타일을 입력하면 Gemini가 국내 여행지를 추천하는 웹서비스입니다.

## 구조는 어떻게 되나요?

```text
HTML/CSS → 화면
JavaScript → 사용자 입력 + fetch()
api/recommend.py → Vercel 백엔드
Gemini API → AI 추천
```

## 새 노트북에서 시작할 때

```bash
python --version
python -m pip install -r requirements.txt
```

그리고 `GEMINI_API_KEY`를 환경 변수에 설정합니다.

## 중요한 주의사항

API Key를 코드나 GitHub에 직접 작성하지 않습니다.

## 과제 발표 때 한 문장 설명

“사용자가 웹 화면에서 여행 정보를 입력하면 JavaScript가 fetch로 Vercel Python API를 호출하고, Python이 Gemini API를 호출한 뒤 JSON 결과를 JavaScript가 화면에 보여주는 구조입니다.”
