# AI 국내 여행 플래너

**과제 제출자 : 신 재 풍**

## 서비스 소개

여행 날짜와 여행 스타일을 입력하면 Gemini API가 국내 여행지를 2~3곳 추천해 주는 바닐라 HTML/CSS/JavaScript 웹서비스입니다.

브라우저의 JavaScript가 `/api/recommend`로 요청을 보내고, Vercel Python Serverless Function이 Gemini API를 호출한 뒤 JSON 결과를 반환합니다. 결과는 JavaScript가 여행지 카드와 하루 여행 예시로 화면에 표시합니다.
## 제출물



## 기술 스택

- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Vercel Functions (Python)
- AI: Google Gemini API
- Deployment: Vercel
- Version control: Git / GitHub

## 배포 URL

```text
Vercel: 배포 후 발급된 URL을 여기에 기록
```

## 화면 구성

### 1. 홈
서비스 소개와 AI 추천 시작 버튼을 제공합니다.

### 2. AI 여행 추천
여행 날짜와 여행 스타일을 입력하고 AI 추천을 요청합니다.

### 3. 여행 정보
추천 결과, 여행 포인트, 오전/오후/저녁 하루 여행 예시를 보여줍니다.

## AI 기능 흐름

```text
사용자 입력
   ↓
JavaScript fetch()
   ↓
POST /api/recommend
   ↓
Vercel Python Serverless Function
   ↓
Gemini API
   ↓
JSON 응답
   ↓
JavaScript가 화면에 출력
```

## 오류 처리

- 빈 입력: 입력 안내 메시지를 표시합니다.
- API 4xx/5xx 또는 서버 예외: 다시 시도 안내 메시지를 표시합니다.
- 응답 지연: 18초 타임아웃 후 다시 시도 안내를 표시합니다.
- Gemini JSON 형식 오류: 서버에서 응답 구조를 검증하고 오류를 반환합니다.

## 환경 변수

API Key는 코드에 직접 작성하지 않습니다.

로컬에서는 `.env` 또는 운영체제 환경 변수로 관리합니다.

Vercel 배포에서는 Project Settings → Environment Variables에서 다음 값을 설정합니다.

```text
GEMINI_API_KEY=발급받은_Gemini_API_Key
```

API Key는 GitHub 저장소, README, 스크린샷에 공개하지 않습니다.

## 로컬 실행

Python 3.12 이상 권장.

```bash
python -m pip install -r requirements.txt
```

환경 변수 설정 후 정적 파일은 로컬 웹서버로 확인할 수 있습니다.

```bash
python -m http.server 8000
```

브라우저에서 `http://localhost:8000` 접속.

> `/api/recommend`는 Vercel Functions 환경에서 실행되므로 AI API 기능 최종 확인은 Vercel 배포 환경에서 진행합니다.

## Vercel 배포

1. GitHub 저장소에 프로젝트를 업로드합니다.
2. Vercel에서 GitHub 저장소를 Import합니다.
3. Environment Variables에 `GEMINI_API_KEY`를 추가합니다.
4. Deploy를 실행합니다.
5. 배포 URL에서 홈 → AI 여행 추천 → 여행 정보 메뉴 이동과 AI 입력/출력을 확인합니다.

Vercel의 Python Runtime은 프로젝트 루트의 `api/` 디렉터리 아래 Python 함수를 Vercel Function으로 배포할 수 있으며, `requirements.txt`로 의존성을 정의할 수 있습니다.

## 제출 전 체크리스트

- [ ] Vercel URL 접속 가능
- [ ] 최소 3개 섹션 메뉴 이동 확인
- [ ] 데스크톱 화면 확인
- [ ] 모바일 화면 확인
- [ ] AI 입력 → 결과 출력 확인
- [ ] 빈 입력 안내 확인
- [ ] API 오류 안내 확인
- [ ] README에 배포 URL 기록
- [ ] 서비스 기획서 포함
- [ ] 데스크톱/모바일/AI 동작 스크린샷 준비
- [ ] AI 코딩 도구 사용 과정 증빙 준비
