import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from api.recommend.index import process_recommend_request

ROOT = Path(__file__).resolve().parent


class AppHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") == "/api/recommend":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 20_000:
                    self.send_json(400, {"error": "요청 데이터가 올바르지 않습니다."})
                    return

                raw = self.rfile.read(length).decode("utf-8")
                payload = json.loads(raw)
                data = process_recommend_request(payload)
                self.send_json(200, data)
            except json.JSONDecodeError:
                self.send_json(502, {"error": "AI 응답을 JSON으로 해석하지 못했습니다. 잠시 후 다시 시도해 주세요."})
            except ValueError as exc:
                self.send_json(400, {"error": str(exc)})
            except RuntimeError as exc:
                self.send_json(500, {"error": str(exc)})
            except Exception:
                self.send_json(502, {"error": "AI API 호출 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."})
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "요청 경로를 찾을 수 없습니다."}, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path.rstrip("/") == "/api/recommend":
            self.send_json(405, {"error": "이 엔드포인트는 POST만 지원합니다."})
            return
        return super().do_GET()

    def send_json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def log_message(self, format: str, *args):
        pass


def create_server(host: str = "0.0.0.0", port: int = 8000):
    os.chdir(ROOT)
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Serving HTTP on http://localhost:{port}")
    return server


if __name__ == "__main__":
    create_server().serve_forever()
