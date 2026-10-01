import json
import os
from http.server import BaseHTTPRequestHandler

from google import genai


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
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


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

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
            date_text = str(payload.get("date", "")).strip()
            style = str(payload.get("style", "")).strip()

            if not date_text or not style:
                send_json(self, 400, {"error": "여행 날짜와 여행 스타일을 모두 입력해 주세요."})
                return
            if len(style) > 300:
                send_json(self, 400, {"error": "여행 스타일은 300자 이내로 입력해 주세요."})
                return

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                send_json(self, 500, {"error": "서버에 GEMINI_API_KEY가 설정되지 않았습니다."})
                return

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

            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt,
            )
            text = interaction.output_text
            data = parse_json_response(text)
            send_json(self, 200, data)

        except json.JSONDecodeError:
            send_json(self, 502, {"error": "AI 응답을 JSON으로 해석하지 못했습니다. 잠시 후 다시 시도해 주세요."})
        except ValueError as exc:
            send_json(self, 502, {"error": str(exc)})
        except Exception:
            send_json(self, 502, {"error": "AI API 호출 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."})
