# AI 국내 여행 플래너

**과제 제출자 : 신 재 풍**

## 서비스 소개

여행 날짜와 여행 스타일을 입력하면 Gemini API가 국내 여행지를 2~3곳 추천해 주는 바닐라 HTML/CSS/JavaScript 웹서비스입니다.

브라우저의 JavaScript가 `/api/recommend`로 요청을 보내고, Vercel Python Serverless Function이 Gemini API를 호출한 뒤 JSON 결과를 반환합니다. 결과는 JavaScript가 여행지 카드와 하루 여행 예시로 화면에 표시합니다.

## 제출물

### 1 AI국내여행 메뉴화면 :

![AI국내여행](여행날짜_스크린샷.png)

### 2 AI국내여행 메뉴화면 :

![AI국내여행](여행지_스크린샷.png)

### 3 AI국내여행 메뉴화면 :

![AI국내여행](다음주말_스크린샷.png)

### 4 AI국내여행 [날짜와 지역을 선택한] 실행 결과 :

![AI국내여행](국내여행.png)


## 기술 스택

- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Vercel Functions (Python)
- AI: Google Gemini API
- Deployment: Vercel
- Version control: Git / GitHub

## 배포 URL

```text
Vercel 배포는 로컬에서 준비 완료 상태이며, 실제 배포는 Vercel 로그인 후 아래 명령으로 진행합니다.

npx vercel login
npx vercel --prod
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

로컬에서는 `.env` 또는 운영체제 환경 변수로 관리합니다. 예시는 `.env.example` 파일을 참고하세요.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Vercel 배포에서는 Project Settings → Environment Variables에서 동일한 값을 추가합니다.

`GEMINI_MODEL`은 선택 사항이며, 무료 API 키를 사용할 때는 `gemini-3.5-flash-lite` → `gemini-3.5-flash` → `gemini-3.8-flash` 순으로 자동으로 대체됩니다.

API Key는 GitHub 저장소, README, 스크린샷에 공개하지 않습니다.

## 로컬 실행

Python 3.12 이상 권장.

```bash
python -m pip install -r requirements.txt
```

환경 변수 설정 후 정적 파일은 로컬 웹서버로 확인할 수 있습니다.

### 웹 브라우저로 실행

```bash
python server.py
```

브라우저에서 `http://localhost:8000` 접속.

### PyQt5 데스크톱 앱으로 실행

```bash
python desktop_app.py
```

이 앱은 프로젝트의 로컬 서버를 자동으로 실행하고, 내장 브라우저에서 전체 웹 화면을 보여줍니다.

> 로컬에서는 정적 파일과 `/api/recommend` API를 함께 처리하는 서버를 실행합니다. 실제 AI 호출은 `GEMINI_API_KEY` 환경 변수가 있어야 동작합니다.

## Vercel 배포

1. Vercel에 로그인합니다.
2. 이 저장소를 Import합니다.
3. Project Settings → Environment Variables에서 `GEMINI_API_KEY`와 필요 시 `GEMINI_MODEL`을 추가합니다.
4. Deploy를 실행합니다.
5. 배포 URL에서 홈 → AI 여행 추천 → 여행 정보 메뉴 이동과 AI 입력/출력을 확인합니다.

Vercel의 Python Runtime은 프로젝트 루트의 `api/` 디렉터리 아래 Python 함수를 Vercel Function으로 배포할 수 있으며, `requirements.txt`로 의존성을 정의할 수 있습니다.

실제 배포 명령은 다음과 같습니다.

```bash
npx vercel login
npx vercel --prod
```
