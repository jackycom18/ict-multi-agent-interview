# AI 面试天团架构

```text
候选人
  ↓
interview-orchestrator（唯一发言人与流程调度）
  ├─ general-chat-officer      破冰、公司信息
  ├─ technical-interview-officer  5 道技术题、逐题评分
  ├─ hr-interview-officer      3 道 HR 题、逐题评分
  └─ talent-assessment-specialist  加权计算、HTML 报告
```

流程严格串行：每个 Agent 完成后发送 `CONTROL_RETURN`，Leader 收到信号
后才激活下一角色。最终由人才测评专员按照 70% 技术 + 30% HR 计算综合分。

本次演示候选人：陈星河  
面试岗位：AI Agent 工程师  
面试结果：综合 8.1，强烈推荐。
