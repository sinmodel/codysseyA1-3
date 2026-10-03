import importlib.util
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


if __name__ == "__main__":
    unittest.main()
