"""验证多 Agent 面试工作流、记录和综合评分报告。"""
import tempfile
import unittest
from pathlib import Path

from scripts.run_interview import run_interview

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "interview_dataset.json"


class InterviewWorkflowTest(unittest.TestCase):
    """覆盖五 Agent 协作产物和加权评分。"""

    def test_generates_complete_interview_package(self):
        """功能：验证完整面试产物；输入：无；输出：无。"""
        with tempfile.TemporaryDirectory(prefix="interview-test-") as temp_dir:
            temp_path = Path(temp_dir)
            result = run_interview(
                DATASET,
                output_root=temp_path / "interview_Log",
                archive_dir=temp_path / "作品",
            )

            self.assertEqual(result["technical_average"], 8.0)
            self.assertEqual(result["hr_average"], 8.3)
            self.assertEqual(result["composite_score"], 8.1)
            self.assertEqual(result["rating"], "强烈推荐")
            self.assertEqual(result["technical_count"], 5)
            self.assertEqual(result["hr_count"], 3)
            self.assertEqual(
                sorted(path.name for path in (temp_path / "作品").iterdir()),
                sorted(
                    [
                        "Agent办公实践AI面试协同团队实践.md",
                        "readme.md",
                        result["technical_file"].name,
                        result["hr_file"].name,
                        result["report_file"].name,
                    ]
                ),
            )

            report = result["report_file"].read_text(encoding="utf-8")
            self.assertNotIn("{候选人姓名}", report)
            self.assertIn("陈星河", report)
            self.assertIn("AI Agent工程师", report)
            self.assertIn("strong", result["dialogue_file"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
