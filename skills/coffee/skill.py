# Coffee Skill 注册模块
# 读取 doc/my-coffee/SKILL.md 中的业务规则，注册到 SkillRegistry
import os

from skills.registry import SkillConfig, registry
from config.settings import Config
from utils.logger import LoggerManager

logger = LoggerManager.get_logger()


def _load_skill_instruction() -> str:
    """从 SKILL.md 文件加载 skill 的系统指令"""
    skill_md_path = os.path.join(Config.SKILL_DOC_DIR, "my-coffee", "SKILL.md")
    if not os.path.exists(skill_md_path):
        logger.warning(f"SKILL.md 文件不存在: {skill_md_path}")
        return ""

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 去掉 YAML front matter（---之间的内容），只保留 Markdown 正文
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    return content


def _build_mcp_config() -> dict:
    """构建 my-coffee 的 MCP 连接配置"""
    token = Config.LUCKIN_MCP_TOKEN
    if not token:
        # 尝试从本地文件读取 token
        token_file = os.path.expanduser("~/.my-coffee/LUCKIN_MCP_TOKEN")
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()
            logger.info("从本地文件读取 LUCKIN_MCP_TOKEN")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        logger.warning("LUCKIN_MCP_TOKEN 未配置，MCP 调用将失败")

    return {
        "my-coffee": {
            "url": Config.LUCKIN_MCP_URL,
            "transport": "streamable_http",
            "headers": headers,
        }
    }


def register_coffee_skill():
    """注册咖啡下单 skill"""
    skill = SkillConfig(
        name="my-coffee",
        description="瑞幸咖啡下单助手：查询门店、搜索商品、自提下单、支付、订单查询与取消",
        keywords=[
            "瑞幸", "luckin", "咖啡", "果茶", "轻乳茶",
            "果蔬茶", "柠檬茶", "点单", "下单", "门店",
            "取餐码", "订单状态", "取消订单",
        ],
        mcp_servers=_build_mcp_config(),
        system_instruction=_load_skill_instruction(),
        instruction_only=True,
    )
    registry.register(skill)
    logger.info("咖啡下单 skill 注册完成")


# 模块导入时自动注册
register_coffee_skill()
