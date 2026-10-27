# Agent 办公实践 AI 面试协同团队

本项目对应华为 ICT 2026 云赛道实践赛第 15 题：
“多 Agent 面试协同团队实践”。

项目基于官方 `ai-interview-swarm` 的五个 Agent：

- `interview-orchestrator`：面试调度总控，只由 Leader 对候选人说话。
- `general-chat-officer`：破冰聊天与公司信息答疑。
- `technical-interview-officer`：技术题提问与评分。
- `hr-interview-officer`：HR 综合题提问与评分。
- `talent-assessment-specialist`：加权评分并生成 HTML 报告。

## 实现方式

为满足免费资源约束并保证结果可复现，本项目使用确定性候选人答案驱动
完整多 Agent 串行流程。每个 Agent 仍遵循官方 Skill 的职责、信号格式
和交接顺序；知识库与报告模板来自官方仓库。

综合得分公式：

```text
技术平均分 × 0.7 + HR 平均分 × 0.3
```

当前演示结果：

- 技术得分：`8, 8, 7, 9, 8`，平均 `8.0`
- HR 得分：`8, 9, 8`，平均 `8.3`
- 综合得分：`8.1`
- 综合评级：`强烈推荐`

## 运行

```powershell
python -X utf8 scripts/run_interview.py
```

输出会写入 `interview_Log/`，同时归档到：

```text
Agent办公实践AI面试协同团队实践作品/
```

## 测试

```powershell
python -X utf8 -m unittest discover -s tests -v
```

测试验证五 Agent 产物数量、技术/HR/综合评分、报告占位符替换和完整
对话记录。

## 目录

- `skills/`：官方五 Agent Skill，知识库和输出路径已改为 `/var` 部署口径。
- `knowledge/`：官方四份 PDF 知识库。
- `data/interview_dataset.json`：候选人、题目、答案与评分数据。
- `scripts/run_interview.py`：确定性多 Agent 面试执行器。
- `interview_Log/`：技术面试、HR 面试和综合报告。
- `Agent办公实践AI面试协同团队实践作品/`：比赛要求归档文件。
