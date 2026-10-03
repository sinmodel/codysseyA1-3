import importlib.util
import io
import json
import unittest
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "api" / "recommend" / "index.py"
spec = importlib.util.spec_from_file_location("recommend_index", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GeminiModelFallbackTests(unittest.TestCase):
    def test_free_tier_model_candidates_are_prioritized(self):
        candidates = module.get_model_candidates()
        self.assertEqual(candidates[0], "gemini-3.5-flash-lite")
        self.assertIn("gemini-3.5-flash", candidates)
        self.assertIn("gemini-3.8-flash", candidates)

    def test_quota_error_uses_next_model(self):
        error = Exception("429 Quota exceeded")
        next_model = module.select_next_model("gemini-3.5-flash-lite", error)
        self.assertEqual(next_model, "gemini-3.5-flash")

    def test_get_request_to_api_route_returns_method_error(self):
        request = module.handler.__new__(module.handler)
        request.path = "/api/recommend"
        request.wfile = io.BytesIO()

        status = {}
        headers = {}

        def send_response(code):
            status["code"] = code

        def send_header(key, value):
            headers.setdefault(key, []).append(value)

        def end_headers():
            pass

        request.send_response = send_response
        request.send_header = send_header
        request.end_headers = end_headers

        request.do_GET()

        self.assertEqual(status["code"], 405)
        payload = json.loads(request.wfile.getvalue().decode("utf-8"))
        self.assertEqual(payload["error"], "이 엔드포인트는 POST만 지원합니다.")


if __name__ == "__main__":
    unittest.main()
