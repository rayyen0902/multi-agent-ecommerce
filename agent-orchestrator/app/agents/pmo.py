"""PMO Agent - 项目管理办公室（任务分解、分发、验收）"""
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.blackboard.models import (
    BlackboardEntry,
    EntryType,
    ReviewResult,
    SubTask,
    SubTaskStatus,
    TaskPlan,
)
from app.blackboard.service import BlackboardService
from app.llm.router import ModelRouter
from app.prompts.pmo import PMO_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# 验收评分阈值
REVIEW_PASS_SCORE = 7.0
MAX_REVISIONS = 3


class PMOAgent:
    """PMO Agent：负责任务分解、分发给执行 Agent、验收结果"""

    def __init__(
        self,
        model_router: ModelRouter,
        blackboard: BlackboardService,
        execution_agents: dict,
    ):
        """
        Args:
            model_router: 模型路由器
            blackboard: 黑板服务
            execution_agents: {agent_name: compiled_agent} 执行 Agent 字典
        """
        self.model = model_router.get_model("pmo")
        self.review_model = model_router.get_model("pmo", scenario="pmo_review")
        self.blackboard = blackboard
        self.execution_agents = execution_agents

    async def decompose_task(
        self, session_id: str, intent: dict
    ) -> TaskPlan:
        """根据用户意图分解任务"""
        prompt = f"""请根据以下用户意图，分解为可执行的子任务。

## 用户意图
- 类别: {intent.get('intent_category', 'general_query')}
- 摘要: {intent.get('intent_summary', '')}
- 提取实体: {json.dumps(intent.get('extracted_entities', {}), ensure_ascii=False)}

## 可用的执行 Agent
- order_analyst: 订单数据分析、异常检测
- smart_rule: 自然语言定义自动化规则
- customer_service: 客服回复、退换货处理
- data_analyst: 数据分析报告、趋势预测
- ad_manager: 广告投放管理

## 输出格式（JSON）
{{
  "original_intent": "用户原始意图摘要",
  "subtasks": [
    {{
      "agent_name": "目标Agent名称",
      "description": "具体任务描述，包含所有必要的上下文",
      "dependencies": []
    }}
  ]
}}
"""
        response = await self.model.ainvoke([
            SystemMessage(content=PMO_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        plan_data = self._parse_json(response.content)
        subtasks = [
            SubTask(
                agent_name=st.get("agent_name", "order_analyst"),
                description=st.get("description", ""),
                dependencies=st.get("dependencies", []),
            )
            for st in plan_data.get("subtasks", [])
        ]

        task_plan = TaskPlan(
            session_id=session_id,
            original_intent=intent.get("intent_summary", ""),
            subtasks=subtasks,
        )

        # 写入黑板
        await self.blackboard.write(BlackboardEntry(
            session_id=session_id,
            entry_type=EntryType.TASK_PLAN,
            key="latest",
            value=task_plan.model_dump(),
            author_agent="pmo",
        ))

        # 持久化
        await self.blackboard.save_task_plan(task_plan)

        return task_plan

    async def execute_subtask(
        self, session_id: str, subtask: SubTask, context: dict = None
    ) -> str:
        """将子任务分发给对应执行 Agent"""
        agent_name = subtask.agent_name
        agent = self.execution_agents.get(agent_name)

        if not agent:
            return f"错误: 找不到执行 Agent '{agent_name}'"

        # 构建任务指令
        task_prompt = subtask.description
        if context:
            task_prompt += f"\n\n## 上下文信息\n{json.dumps(context, ensure_ascii=False)}"

        # 写入分配记录
        await self.blackboard.write(BlackboardEntry(
            session_id=session_id,
            entry_type=EntryType.TASK_ASSIGNMENT,
            key=subtask.task_id,
            value={"agent": agent_name, "description": subtask.description},
            author_agent="pmo",
        ))

        # 执行
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=task_prompt)]
        })

        # 提取最后一条消息作为结果
        result_text = ""
        if result.get("messages"):
            for msg in reversed(result["messages"]):
                if hasattr(msg, "content") and msg.content:
                    result_text = msg.content
                    break

        # 写入结果
        await self.blackboard.write(BlackboardEntry(
            session_id=session_id,
            entry_type=EntryType.TASK_RESULT,
            key=subtask.task_id,
            value=result_text,
            author_agent=agent_name,
        ))

        return result_text

    async def review_result(
        self,
        session_id: str,
        subtask: SubTask,
        result_text: str,
        intent: dict,
    ) -> ReviewResult:
        """PMO 验收评估"""
        review_prompt = f"""请评估以下任务执行结果是否达标：

## 原始用户意图
{intent.get('intent_summary', '')}

## 子任务描述
{subtask.description}

## 执行结果
{result_text}

## 验收维度
1. 数据准确性（4分）：结果中的数据是否来自真实系统数据？
2. 完整性（2.5分）：是否回答了用户问题的所有方面？
3. 可操作性（2分）：建议是否具体可执行？
4. 格式规范（1.5分）：输出是否清晰易读？

请以 JSON 格式输出：
{{"approved": true/false, "score": 0到10, "issues": ["问题1", "问题2"], "revision_guidance": "修改建议"}}
"""
        response = await self.review_model.ainvoke([
            SystemMessage(content=PMO_SYSTEM_PROMPT),
            HumanMessage(content=review_prompt),
        ])

        review_data = self._parse_json(response.content)
        review = ReviewResult(
            approved=review_data.get("approved", False),
            score=review_data.get("score", 0),
            issues=review_data.get("issues", []),
            revision_guidance=review_data.get("revision_guidance", ""),
        )

        # 写入黑板
        await self.blackboard.write(BlackboardEntry(
            session_id=session_id,
            entry_type=EntryType.REVIEW_RESULT,
            key=subtask.task_id,
            value=review.model_dump(),
            author_agent="pmo",
        ))

        return review

    async def orchestrate(
        self, session_id: str, intent: dict
    ) -> str:
        """完整编排流程：分解 -> 执行 -> 验收 -> 汇总"""
        # 1. 分解任务
        task_plan = await self.decompose_task(session_id, intent)
        task_plan.status = "executing"

        results = []
        for subtask in task_plan.subtasks:
            # 2. 执行
            result_text = await self.execute_subtask(
                session_id, subtask
            )

            # 3. 验收循环
            for attempt in range(MAX_REVISIONS + 1):
                review = await self.review_result(
                    session_id, subtask, result_text, intent
                )

                if review.approved or review.score >= REVIEW_PASS_SCORE:
                    subtask.status = SubTaskStatus.COMPLETED
                    subtask.result = result_text
                    results.append(result_text)
                    break

                if attempt < MAX_REVISIONS:
                    # 打回重做
                    subtask.status = SubTaskStatus.REVISION
                    subtask.revision_count += 1

                    # 写入修改建议
                    await self.blackboard.write(BlackboardEntry(
                        session_id=session_id,
                        entry_type=EntryType.REVISION_GUIDANCE,
                        key=subtask.task_id,
                        value={
                            "attempt": attempt + 1,
                            "issues": review.issues,
                            "guidance": review.revision_guidance,
                        },
                        author_agent="pmo",
                    ))

                    # 带修改建议重新执行
                    result_text = await self.execute_subtask(
                        session_id,
                        subtask,
                        context={"revision_guidance": review.revision_guidance},
                    )
                else:
                    # 超过重试上限
                    subtask.status = SubTaskStatus.FAILED
                    results.append(
                        f"[任务未达标] {subtask.description}\n"
                        f"原因: {'; '.join(review.issues)}\n"
                        f"结果: {result_text}"
                    )

        # 4. 汇总最终响应
        final_response = self._synthesize_response(task_plan, results)

        await self.blackboard.write(BlackboardEntry(
            session_id=session_id,
            entry_type=EntryType.FINAL_RESPONSE,
            key="latest",
            value=final_response,
            author_agent="pmo",
        ))

        # 更新任务计划状态
        task_plan.status = "completed"
        await self.blackboard.save_task_plan(task_plan)
        await self.blackboard.update_session_status(session_id, "completed")

        return final_response

    @staticmethod
    def _synthesize_response(task_plan: TaskPlan, results: list[str]) -> str:
        """将多个子任务结果整合为最终回复"""
        if len(results) == 1:
            return results[0]

        sections = []
        for i, (subtask, result) in enumerate(
            zip(task_plan.subtasks, results), 1
        ):
            status_icon = "✅" if subtask.status == SubTaskStatus.COMPLETED else "⚠️"
            sections.append(
                f"### {status_icon} 任务 {i}: {subtask.description}\n\n{result}"
            )

        return "\n\n---\n\n".join(sections)

    @staticmethod
    def _parse_json(content: str) -> dict:
        """解析 JSON，处理 markdown 代码块包裹"""
        content = content.strip()
        if content.startswith("```"):
            parts = content.split("```")
            content = parts[1] if len(parts) > 1 else parts[0]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"PMO JSON 解析失败: {content[:200]}")
            return {}
