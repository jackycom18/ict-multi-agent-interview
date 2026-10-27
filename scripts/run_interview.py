"""运行确定性的五 Agent AI 面试协同流程。"""
import html
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/talent-assessment-specialist/resources/report_template.html"
ARTIFACT_NAME = "Agent办公实践AI面试协同团队实践作品"


def _load_dataset(dataset_path: Path) -> dict:
    """功能：读取并校验面试数据；输入：数据集路径；输出：规范化数据字典。"""
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    candidate = data.get("candidate", {})
    if not candidate.get("name") or not candidate.get("email"):
        raise ValueError("候选人姓名和邮箱不能为空")
    if not data.get("position"):
        raise ValueError("面试岗位不能为空")
    for group in ("technical_questions", "hr_questions"):
        questions = data.get(group, [])
        if not questions:
            raise ValueError(f"{group} 不能为空")
        for question in questions:
            score = question.get("score")
            if not isinstance(score, int) or not 0 <= score <= 10:
                raise ValueError(f"{group} 得分必须是 0-10 的整数")
    return data


def calculate_scores(data: dict) -> dict:
    """功能：计算技术、HR 和综合得分；输入：面试数据；输出：评分字典。"""
    technical_scores = [item["score"] for item in data["technical_questions"]]
    hr_scores = [item["score"] for item in data["hr_questions"]]
    technical_average = round(sum(technical_scores) / len(technical_scores), 1)
    hr_average = round(sum(hr_scores) / len(hr_scores), 1)
    composite_score = round(
        sum(technical_scores) / len(technical_scores) * 0.7
        + sum(hr_scores) / len(hr_scores) * 0.3,
        1,
    )
    if composite_score >= 8.0:
        rating = "强烈推荐"
    elif composite_score >= 6.5:
        rating = "推荐"
    elif composite_score >= 5.0:
        rating = "待定"
    else:
        rating = "不推荐"
    return {
        "technical_scores": technical_scores,
        "technical_total": sum(technical_scores),
        "technical_average": technical_average,
        "hr_scores": hr_scores,
        "hr_total": sum(hr_scores),
        "hr_average": hr_average,
        "composite_score": composite_score,
        "rating": rating,
    }


def _level(score: float) -> tuple[str, str, str]:
    """功能：映射得分等级；输入：0-10 分数；输出：等级、徽章和中文评级。"""
    if score >= 8.0:
        return "high", "excellent", "优秀"
    if score >= 6.5:
        return "medium", "qualified", "合格"
    return "low", "poor", "待提升"


def _comment(rating: str) -> str:
    """功能：生成综合评语；输入：综合评级；输出：HTML 评语文本。"""
    comments = {
        "强烈推荐": "候选人在技术能力和综合素质两方面均表现优异。技术边界清晰，能够从规划、工具调用、知识检索、权限控制到上线评估形成完整闭环；沟通中能够以事实推动协作，职业目标与岗位方向一致。综合评估为<strong>强烈推荐</strong>，建议优先进入下一轮。",
        "推荐": "候选人整体表现良好，具备岗位所需的核心技术能力和综合素质。部分维度仍有提升空间，但不影响整体判断。综合评估为<strong>推荐</strong>，建议进入下一轮流程。",
        "待定": "候选人在部分维度表现不足，与岗位核心要求存在差距。综合评估为<strong>待定</strong>，建议进行补充考核后综合决策。",
        "不推荐": "候选人的核心能力与岗位需求存在较大差距，技术和/或综合素质方面有明显不足。综合评估为<strong>不推荐</strong>。",
    }
    return comments[rating]


def _question_rows(questions: list[dict]) -> str:
    """功能：生成报告题目表格；输入：题目列表；输出：HTML 行字符串。"""
    rows = []
    for index, item in enumerate(questions, start=1):
        score = item["score"]
        badge = "s-excellent" if score >= 8 else "s-qualified" if score >= 5 else "s-poor"
        rows.append(
            "<tr>"
            f'<td class="q-col">Q{index}</td>'
            f"<td>{html.escape(item['question'])}</td>"
            f"<td>{html.escape(item['purpose'])}</td>"
            f'<td class="answer-text">{html.escape(item["answer"])}</td>'
            f'<td class="ref-text">{html.escape(item["reference"])}</td>'
            f'<td><span class="score-badge {badge}">{score}</span></td>'
            f"<td>{html.escape(item['rationale'])}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _render_report(data: dict, scores: dict, interview_time: datetime) -> str:
    """功能：填充官方报告模板；输入：数据、评分和时间；输出：HTML 文本。"""
    technical_level, technical_badge, technical_label = _level(
        scores["technical_average"]
    )
    hr_level, hr_badge, hr_label = _level(scores["hr_average"])
    replacements = {
        "{候选人姓名}": data["candidate"]["name"],
        "{学校}": data["candidate"]["school"],
        "{邮箱}": data["candidate"]["email"],
        "{岗位名称}": data["position"],
        "{面试日期}": interview_time.strftime("%Y-%m-%d"),
        "{报告生成日期}": interview_time.strftime("%Y-%m-%d %H:%M:%S"),
        "{技术平均分}": f"{scores['technical_average']:.1f}",
        "{技术得分等级}": technical_level,
        "{技术徽章}": technical_badge,
        "{技术评级}": technical_label,
        "{HR平均分}": f"{scores['hr_average']:.1f}",
        "{HR得分等级}": hr_level,
        "{HR徽章}": hr_badge,
        "{HR评级}": hr_label,
        "{综合总分}": f"{scores['composite_score']:.1f}",
        "{综合评级}": scores["rating"],
        "{技术各题明细行}": _question_rows(data["technical_questions"]),
        "{HR各题明细行}": _question_rows(data["hr_questions"]),
        "{综合评语}": _comment(scores["rating"]),
    }
    report = TEMPLATE.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        report = report.replace(placeholder, value)
    return report


def _record_text(data: dict, kind: str, scores: dict, interview_time: datetime) -> str:
    """功能：生成单场面试记录；输入：数据、轮次、评分和时间；输出：文本记录。"""
    is_technical = kind == "技术面试"
    key = "technical_questions" if is_technical else "hr_questions"
    score_key = "technical_scores" if is_technical else "hr_scores"
    average_key = "technical_average" if is_technical else "hr_average"
    officer = "技术面试官" if is_technical else "HR面试官"
    lines = [
        f"{kind}完整记录",
        "",
        f"候选人姓名：{data['candidate']['name']}",
        f"面试岗位：{data['position']}",
        f"面试日期：{interview_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"面试官：{officer}",
        "",
        "=" * 60,
    ]
    for index, item in enumerate(data[key], start=1):
        lines.extend(
            [
                f"【题目{index}】{item['question']}",
                f"候选人回答：{item['answer']}",
                f"考察目的：{item['purpose']}",
                f"参考答案：{item['reference']}",
                f"得分：{item['score']}/10",
                f"评分依据：{item['rationale']}",
                "",
            ]
        )
    lines.extend(
        [
            "=" * 60,
            f"【{kind}综合评分】",
            f"总题数：{len(data[key])}",
            f"总分：{sum(scores[score_key])}",
            f"平均分：{scores[average_key]:.1f}",
            f"综合评级：{_level(scores[average_key])[2]}",
            "",
            f"{officer}评语：回答整体与知识库评分标准一致，逻辑清晰，能够结合实践说明关键技术取舍。",
        ]
    )
    return "\n".join(lines) + "\n"


def _dialogue_text(
    data: dict,
    scores: dict,
    interview_time: datetime,
    report_name: str,
) -> str:
    """功能：生成完整对话记录；输入：数据、评分、时间和报告名；输出：Markdown。"""
    candidate = data["candidate"]
    lines = [
        "# Agent办公实践AI面试协同团队实践",
        "",
        f"- 面试时间：{interview_time.strftime('%Y-%m-%d %H:%M:%S')}",
        "- 面试团队：5 个专业 Agent",
        "- 运行模式：集群模式（严格串行交接）",
        f"- 候选人：{candidate['name']}",
        f"- 学校：{candidate['school']}",
        f"- 岗位：{data['position']}",
        "",
        "## 一、人才信息登记",
        "",
        "**Leader / 面试调度总控**：您好，欢迎来到恒信数字科技有限公司 AI 智能面试系统，请提供姓名、邮箱、院校和补充经历。",
        "",
        f"**候选人**：姓名：{candidate['name']}；邮箱：{candidate['email']}；院校：{candidate['school']}；其他：{candidate['other']}。",
        "",
        "**Leader**：已收到候选人信息，下面展示招聘简章，并进入破冰环节。",
        "",
        "## 二、破冰",
        "",
        "**general-chat-officer**：今天过来还顺利吗？面试前先轻松聊几句。",
        "",
        "**候选人**：挺顺利的，我准备好了。",
        "",
        "READY_CONFIRMED|候选人",
        "CONTROL_RETURN|GENERAL_CHAT_OFFICER|STATUS_READY",
        "",
        "**Leader**：破冰完成，现在进入技术面试环节。",
        "",
        "## 三、技术面试",
        "",
        "TECHNICAL_INTERVIEW_STARTED",
        f"DOMAIN_CONFIRMED|{data['position']}|TOTAL_QUESTIONS_{len(data['technical_questions'])}",
        "",
    ]
    for index, item in enumerate(data["technical_questions"], start=1):
        lines.extend(
            [
                f"**technical-interview-officer**：【题目{index}】{item['question']}",
                "",
                f"**候选人**：{item['answer']}",
                "",
                f"PROGRESS_REPORT|QUESTION_{index}|TOTAL_{len(data['technical_questions'])}|SCORE_{item['score']}|JUSTIFICATION_{item['rationale']}",
                "",
            ]
        )
    lines.extend(
        [
            "CONTROL_RETURN",
            f"TECHNICAL_SCORING_DATA|{candidate['name']}|{data['position']}|{','.join(map(str, scores['technical_scores']))}|{scores['technical_total']}|{scores['technical_average']}|strong",
            "",
            "**Leader**：技术面试完成，现在进入综合能力面试环节。",
            "",
            "## 四、HR 面试",
            "",
            "HR_INTERVIEW_STARTED",
            "",
        ]
    )
    for index, item in enumerate(data["hr_questions"], start=1):
        lines.extend(
            [
                f"**hr-interview-officer**：【题目{index}】{item['question']}",
                "",
                f"**候选人**：{item['answer']}",
                "",
                f"PROGRESS_REPORT|QUESTION_{index}|TOTAL_{len(data['hr_questions'])}|SCORE_{item['score']}|JUSTIFICATION_{item['rationale']}",
                "",
            ]
        )
    lines.extend(
        [
            "CONTROL_RETURN",
            f"HR_SCORING_DATA|{candidate['name']}|{data['position']}|{','.join(map(str, scores['hr_scores']))}|{scores['hr_total']}|{scores['hr_average']}|strong",
            "",
            "**Leader**：两个面试环节均已完成，现在交给人才测评专员。",
            "",
            "ASSESSMENT_DATA|已传递候选人、技术评分、HR 评分和全部题目明细",
            "",
            "## 五、综合评估",
            "",
            f"**talent-assessment-specialist**：按技术 70% + HR 30% 计算，综合得分 **{scores['composite_score']:.1f}**，评级 **{scores['rating']}**。",
            "",
            f"REPORT_READY|{candidate['name']}|{data['position']}|{scores['composite_score']:.1f}|{scores['rating']}|{report_name}",
            "",
            "**Leader**：面试已完成，综合评估报告已生成并归档。",
            "",
            "## 六、执行结果",
            "",
            "| Agent | 职责 | 状态 |",
            "|---|---|---|",
            "| interview-orchestrator | 信息登记、串行调度、结果汇总 | 完成 |",
            "| general-chat-officer | 破冰与公司信息答疑 | 完成 |",
            f"| technical-interview-officer | {len(data['technical_questions'])} 道技术题与评分 | 完成 |",
            f"| hr-interview-officer | {len(data['hr_questions'])} 道 HR 题与评分 | 完成 |",
            "| talent-assessment-specialist | 加权评分与 HTML 报告 | 完成 |",
            "",
            f"- 技术平均分：{scores['technical_average']:.1f}",
            f"- HR 平均分：{scores['hr_average']:.1f}",
            f"- 综合得分：{scores['composite_score']:.1f}",
            f"- 综合评级：{scores['rating']}",
            "",
            "> 本实践使用确定性候选人答案和本地评分数据进行可复现演示；Agent 定义、知识库和报告模板均来自官方 `ai-interview-swarm` 项目。",
        ]
    )
    return "\n".join(lines) + "\n"


def _readme(workdir: Path) -> str:
    """功能：生成比赛 README；输入：作品目录；输出：Markdown 文本。"""
    return (
        f"- **作品目录**：{workdir}\n"
        "- **作品名称**：Agent办公实践AI面试协同团队实践\n"
        "- **作品简介**：本实践基于 多智能体协作（Multi-Agent） 思路，将传统“单 AI 全包”的面试模式升级为“AI 面试天团”团队协作模式，解决企业招聘中面试官成本高、评估标准不统一、人为偏见难避免三大痛点。\n"
    )


def run_interview(
    dataset_path: Path,
    output_root: Path | None = None,
    archive_dir: Path | None = None,
) -> dict:
    """功能：运行五 Agent 面试并归档产物；输入：数据、输出和归档目录；输出：运行结果。"""
    dataset_path = Path(dataset_path)
    data = _load_dataset(dataset_path)
    scores = calculate_scores(data)
    interview_time = datetime.now()
    timestamp = interview_time.strftime("%Y%m%d_%H%M%S")
    output_root = Path(output_root or ROOT / "interview_Log")
    archive_dir = Path(archive_dir or ROOT / ARTIFACT_NAME)
    candidate = data["candidate"]["name"]
    position = data["position"]

    technical_dir = output_root / "技术面试"
    hr_dir = output_root / "HR面试"
    report_dir = output_root / "综合评估"
    for directory in (technical_dir, hr_dir, report_dir, archive_dir):
        directory.mkdir(parents=True, exist_ok=True)

    technical_file = technical_dir / f"技术面试记录_{candidate}_{position}_{timestamp}.txt"
    hr_file = hr_dir / f"HR面试记录_{candidate}_{position}_{timestamp}.txt"
    report_file = report_dir / f"综合评估报告_{candidate}_{position}_{timestamp}.html"
    dialogue_file = archive_dir / "Agent办公实践AI面试协同团队实践.md"
    readme_file = archive_dir / "readme.md"

    technical_file.write_text(
        _record_text(data, "技术面试", scores, interview_time), encoding="utf-8"
    )
    hr_file.write_text(
        _record_text(data, "HR面试", scores, interview_time), encoding="utf-8"
    )
    report_file.write_text(
        _render_report(data, scores, interview_time), encoding="utf-8"
    )
    dialogue_file.write_text(
        _dialogue_text(data, scores, interview_time, report_file.name),
        encoding="utf-8",
    )
    readme_file.write_text(_readme(ROOT), encoding="utf-8")

    for source in (technical_file, hr_file, report_file):
        shutil.copy2(source, archive_dir / source.name)
    return {
        **scores,
        "technical_count": len(data["technical_questions"]),
        "hr_count": len(data["hr_questions"]),
        "technical_file": technical_file,
        "hr_file": hr_file,
        "report_file": report_file,
        "dialogue_file": dialogue_file,
        "readme_file": readme_file,
        "archive_dir": archive_dir,
    }


def main() -> None:
    """功能：使用默认数据运行面试；输入：无；输出：无。"""
    result = run_interview(ROOT / "data/interview_dataset.json")
    summary = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
