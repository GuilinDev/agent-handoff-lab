"""Replay-verification regression: recorded evidence must support every score."""
import json
import unittest
from pathlib import Path
from lab.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]


class RecordedSuiteTests(unittest.TestCase):
    def test_all_recorded_scores_recompute_from_raw_state_evidence(self):
        suite = json.loads((ROOT / "artifacts/suite.json").read_text(encoding="utf8"))
        self.assertEqual(len(suite["runs"]), suite["repeats"] * 3)
        for entry in suite["runs"]:
            with self.subTest(run=entry["id"]):
                run = json.loads((ROOT / "artifacts/runs" / (entry["id"] + ".json")).read_text(encoding="utf8"))
                recomputed = evaluate(run)
                self.assertEqual(recomputed, run["evaluation"])
                for key, value in recomputed.items():
                    self.assertEqual(entry[key], value)
                self.assertEqual(entry["status"] == "passed", recomputed["passed"])


if __name__ == "__main__":
    unittest.main()
