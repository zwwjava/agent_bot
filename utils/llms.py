# LLM 工厂模块 - 统一管理模型实例化
from langchain_openai import ChatOpenAI
from config.settings import Config
from utils.logger import LoggerManager

logger = LoggerManager.get_logger()


class LLMInitializationError(Exception):
    """LLM 初始化异常"""
    pass


def get_llm() -> ChatOpenAI:
    """
    获取对话 LLM 实例
    所有模型配置统一通过环境变量 / .env 文件管理

    Returns:
        ChatOpenAI: 对话模型实例
    """
    try:
        if not Config.LLM_API_KEY:
            raise LLMInitializationError("LLM_API_KEY 未配置，请在 .env 文件中设置")

        llm_chat = ChatOpenAI(
            base_url=Config.LLM_BASE_URL,
            api_key=Config.LLM_API_KEY,
            model=Config.LLM_CHAT_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            timeout=Config.LLM_TIMEOUT,
            max_retries=Config.LLM_MAX_RETRIES,
        )

        logger.info(f"成功初始化 LLM: {Config.LLM_CHAT_MODEL} @ {Config.LLM_BASE_URL}")
        return llm_chat

    except LLMInitializationError:
        raise
    except Exception as e:
        logger.error(f"初始化 LLM 失败: {str(e)}")
        raise LLMInitializationError(f"初始化 LLM 失败: {str(e)}")
