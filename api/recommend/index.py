import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

from google import genai

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

FREE_TIER_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]


def get_model_candidates() -> list[str]:
    configured = (os.getenv("GEMINI_MODEL") or "").strip()
    if configured:
        candidates = [configured]
        for model in FREE_TIER_MODELS:
            if model not in candidates:
                candidates.append(model)
        return candidates
    return list(FREE_TIER_MODELS)


def is_quota_or_model_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = [
        "quota",
        "rate limit",
        "429",
        "resource exhausted",
        "too many requests",
        "model not found",
        "unsupported model",
        "not found",
        "permission denied",
        "forbidden",
    ]
    return any(marker in text for marker in markers)


def select_next_model(current_model: str, exc: Exception) -> str | None:
    if not is_quota_or_model_error(exc):
        return None

    candidates = get_model_candidates()
    if current_model not in candidates:
        return None

    index = candidates.index(current_model)
    if index + 1 >= len(candidates):
        return None
    return candidates[index + 1]


def extract_response_text(response) -> str:
    if response is None:
        raise ValueError("AI 응답이 비어 있습니다.")

    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", None)
    if candidates:
        for candidate in candidates:
            if getattr(candidate, "content", None):
                parts = getattr(candidate.content, "parts", None) or []
                for part in parts:
                    if getattr(part, "text", None):
                        return part.text

    if isinstance(response, str):
        return response

    raise ValueError("AI 응답 텍스트를 추출하지 못했습니다.")


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


def clean_json_text(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].lstrip("\n ")
    return text.strip()


def parse_json_response(text: str) -> dict:
    cleaned = clean_json_text(text)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("AI 응답이 객체 형식이 아닙니다.")

    required = ["recommended_cities", "weather", "events", "reason"]
    for key in required:
        if key not in data:
            raise ValueError(f"필수 항목이 없습니다: {key}")

    cities = data["recommended_cities"]
    if not isinstance(cities, list) or not 2 <= len(cities) <= 3:
        raise ValueError("추천 지역은 2~3개여야 합니다.")
    if not all(isinstance(city, str) and city.strip() for city in cities):
        raise ValueError("추천 지역 이름 형식이 올바르지 않습니다.")
    if not isinstance(data["weather"], str):
        raise ValueError("weather 형식이 올바르지 않습니다.")
    if not isinstance(data["events"], list):
        raise ValueError("events 형식이 올바르지 않습니다.")
    if not isinstance(data["reason"], str):
        raise ValueError("reason 형식이 올바르지 않습니다.")

    itinerary = data.get("itinerary")
    if itinerary is not None and not isinstance(itinerary, dict):
        data["itinerary"] = {}

    return data


def process_recommend_request(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("요청 데이터 형식이 올바르지 않습니다.")

    date_text = str(payload.get("date", "")).strip()
    style = str(payload.get("style", "")).strip()

    if not date_text or not style:
        raise ValueError("여행 날짜와 여행 스타일을 모두 입력해 주세요.")
    if len(style) > 300:
        raise ValueError("여행 스타일은 300자 이내로 입력해 주세요.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("서버에 GEMINI_API_KEY가 설정되지 않았습니다.")

    config_model = (os.getenv("GEMINI_MODEL") or "").strip()
    if config_model:
        model_candidates = [config_model]
        for model in FREE_TIER_MODELS:
            if model not in model_candidates:
                model_candidates.append(model)
    else:
        model_candidates = list(FREE_TIER_MODELS)

    client = genai.Client(api_key=api_key)
    prompt = f"""
당신은 국내 여행 플래너입니다.
사용자의 여행 날짜와 여행 스타일을 바탕으로 국내 여행지를 2~3곳 추천하세요.
초보 여행자가 이해하기 쉬운 짧고 실용적인 설명을 사용하세요.

여행 날짜: {date_text}
여행 스타일: {style}

반드시 아래 JSON 형식의 객체 하나만 출력하세요.
마크다운, 코드 블록, 설명 문장은 넣지 마세요.
{{
  "recommended_cities": ["지역1", "지역2", "지역3"],
  "weather": "계절과 여행 준비에 도움이 되는 일반적인 날씨 설명",
  "events": ["볼거리 또는 여행 포인트 1", "볼거리 또는 여행 포인트 2"],
  "reason": "추천 이유",
  "itinerary": {{
    "morning": "오전 활동",
    "afternoon": "오후 활동",
    "evening": "저녁 활동"
  }}
}}
"""

    last_error = None
    for model_name in model_candidates:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = extract_response_text(response)
            return parse_json_response(text)
        except Exception as exc:  # pragma: no cover - fallback handling
            last_error = exc
            next_model = select_next_model(model_name, exc)
            if next_model is None:
                break
            continue

    if last_error is not None:
        raise last_error
    raise RuntimeError("Gemini 모델 응답을 생성하지 못했습니다.")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") == "/api/recommend":
            send_json(self, 405, {"error": "이 엔드포인트는 POST만 지원합니다."})
            return
        send_json(self, 404, {"error": "요청 경로를 찾을 수 없습니다."})

    def do_POST(self):
        if self.path.rstrip("/") != "/api/recommend":
            send_json(self, 404, {"error": "요청 경로를 찾을 수 없습니다."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 20_000:
                send_json(self, 400, {"error": "요청 데이터가 올바르지 않습니다."})
                return

            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw)
            try:
                data = process_recommend_request(payload)
                send_json(self, 200, data)
            except ValueError as exc:
                send_json(self, 400, {"error": str(exc)})
            except RuntimeError as exc:
                send_json(self, 500, {"error": str(exc)})
            except Exception:
                send_json(self, 502, {"error": "AI API 호출 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."})
        except json.JSONDecodeError:
            send_json(self, 502, {"error": "요청 JSON을 해석하지 못했습니다. 잠시 후 다시 시도해 주세요."})
        except ValueError as exc:
            send_json(self, 502, {"error": str(exc)})
        except Exception:
            send_json(self, 502, {"error": "AI API 호출 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."})
