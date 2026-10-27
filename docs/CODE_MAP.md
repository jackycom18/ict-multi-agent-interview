# 代码地图

> 最后更新：2026-10-27

## 总体结构

```text
multi-agent-interview-practice/
├── skills/                         五个官方 Agent Skill
├── knowledge/                      官方 PDF 知识库
├── data/interview_dataset.json     候选人、题目、答案与评分
├── scripts/run_interview.py        面试执行与归档
├── tests/test_interview_workflow.py
├── interview_Log/                  三类本地输出
├── reports/                        测试与视觉验收
└── Agent办公实践AI面试协同团队实践作品/
```

## 逐文件核心内容

### `scripts/run_interview.py`

- 用途：校验面试数据，计算技术/HR/综合得分，生成记录与 HTML 报告。
- 入口：`run_interview()`、`calculate_scores()`、`_render_report()`。
- 数据流：JSON 数据集 → 五 Agent 对话文本 → 技术/HR 记录 → HTML 报告 → 归档。
- 注意：综合分使用未四舍五入的技术和 HR 原始平均值计算，再统一保留一位小数。

### `tests/test_interview_workflow.py`

- 用途：验证评分、产物集合和报告占位符替换。
- 数据流：临时目录 → `run_interview()` → 检查五份归档文件。

### `skills/*/SKILL.md`

- 用途：定义 Leader、破冰、技术、HR、测评五个 Agent 的职责和信号协议。
- 注意：知识库路径为 `/var/interview_Lab/`，输出路径为 `/var/interview_Log/`。
