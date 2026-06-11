# 智能体主程序 - 组装 Agent、工具、提示词
import asyncio

# 使用 langgraph 的标准 ReAct Agent 创建 API
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver

from config.settings import Config
from utils.llms import get_llm
from utils.logger import LoggerManager
from skills.registry import registry
from mcp_client.client import mcp_factory

logger = LoggerManager.get_logger()


async def build_agent():
    """
    构建智能体实例

    流程：
    1. 初始化 LLM
    2. 触发所有 skill 注册
    3. 初始化 MCP 客户端，获取远程工具
    4. 加载并渲染系统提示词（注入完整 skill 指令）
    5. 构建 chat_prompt 模板（注入 skill 摘要到用户消息）
    6. 创建 Agent

    Returns:
        agent: LangGraph ReAct Agent 实例
        chat_prompt: ChatPromptTemplate 实例（含 skill 摘要上下文）
    """
    # 1. 初始化 LLM
    llm = get_llm()

    # 2. skill 已在 skills/__init__.py 中通过 import 自动注册
    skill_instructions = registry.get_all_system_instructions()
    logger.info(f"已加载 {len(registry.skill_names)} 个 skill: {registry.skill_names}")

    # 3. 初始化 MCP 客户端，获取远程工具
    mcp_tools = await mcp_factory.initialize()

    # 4. 加载系统提示词模板，注入完整 skill 指令
    system_prompt_template = PromptTemplate.from_file(
        template_file=Config.SYSTEM_PROMPT_TMPL,
        encoding="utf-8",
    ).template
    system_prompt = system_prompt_template.format(skill_instructions=skill_instructions)

    # 5. 构建 human_prompt 模板，在用户消息中注入 skill 摘要
    #    注意：system_prompt 不再纳入 ChatPromptTemplate，因为 SKILL.md 中包含 JSON 示例的
    #    大括号会与 f-string 模板语法冲突。系统提示词已通过 create_react_agent(prompt=) 注入。
    human_prompt = PromptTemplate.from_file(
        template_file=Config.HUMAN_PROMPT_TMPL,
        encoding="utf-8",
    ).template

    chat_prompt = ChatPromptTemplate.from_messages([
        ("human", human_prompt),
    ])

    # 6. 创建短期记忆检查点
    checkpointer = InMemorySaver()

    # 7. 创建 ReAct Agent（系统提示词通过 prompt 参数注入）
    agent = create_react_agent(
        model=llm,
        tools=mcp_tools,
        prompt=system_prompt,
        checkpointer=checkpointer,
    )

    logger.info("智能体构建完成")
    return agent, chat_prompt


async def chat(agent, chat_prompt, user_input: str, thread_id: str = None, user_id: str = None):
    """
    与智能体对话

    通过 chat_prompt 模板格式化用户消息，
    将 skill 摘要注入到每次对话中，确保 agent 始终知道自己有哪些技能。

    Args:
        agent: Agent 实例
        chat_prompt: ChatPromptTemplate 实例
        user_input: 用户输入文本
        thread_id: 会话线程 ID
        user_id: 用户 ID

    Returns:
        str: Agent 回复内容
    """
    thread_id = thread_id or Config.AGENT_THREAD_ID
    user_id = user_id or Config.AGENT_USER_ID

    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id,
        }
    }

    # logger.info(f"用户输入: {user_input}")

    # 使用 chat_prompt 模板格式化消息，注入 question
    messages = chat_prompt.format_messages(
        question=user_input,
    )
    # 取出格式化后的用户消息（模板最后一条）
    human_msg = messages[-1]

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": human_msg.content}]},
        config=config,
    )

    result = response["messages"][-1].content
    # logger.info(f"Agent 回复: {result}")
    return result
