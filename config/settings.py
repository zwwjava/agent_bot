# 统一配置模块 - 集中管理所有配置项
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """统一配置类"""

    # ==================== 日志配置 ====================
    LOG_FILE = "logfile/app.log"
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    MAX_BYTES = 5 * 1024 * 1024
    BACKUP_COUNT = 3

    # ==================== LLM 配置 ====================
    LLM_TYPE = os.getenv("LLM_TYPE", "openai")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_CHAT_MODEL = os.getenv("LLM_CHAT_MODEL", "qwen-plus-latest")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))

    # ==================== MCP 配置 ====================
    # 瑞幸咖啡 MCP 远程服务器
    LUCKIN_MCP_URL = os.getenv("LUCKIN_MCP_URL", "https://gwmcp.lkcoffee.com/order/user/mcp")
    LUCKIN_MCP_TOKEN = os.getenv("LUCKIN_MCP_TOKEN", "")

    # ==================== Prompt 配置 ====================
    SYSTEM_PROMPT_TMPL = "prompt/system_prompt_tmpl.md"
    HUMAN_PROMPT_TMPL = "prompt/human_prompt_tmpl.md"

    # ==================== Skill 配置 ====================
    # Skill 文档目录，存放各 skill 的 SKILL.md 等文件
    SKILL_DOC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "doc")

    # ==================== Agent 配置 ====================
    AGENT_THREAD_ID = os.getenv("AGENT_THREAD_ID", "1")
    AGENT_USER_ID = os.getenv("AGENT_USER_ID", "user_001")
