# 智能体主入口 - 交互式命令行对话
import asyncio

from agent import build_agent, chat
from config.settings import Config
from utils.logger import LoggerManager

logger = LoggerManager.get_logger()


async def main():
    """主函数：构建智能体并进入交互式对话循环"""
    print("=" * 50)
    print("  智能生活助手 - 支持咖啡下单等技能")
    print("  输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    # 构建智能体
    agent, chat_prompt = await build_agent()

    # 交互式对话循环
    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        # 调用智能体
        try:
            response = await chat(agent, chat_prompt, user_input)
            print(f"\n助手: {response}")
        except Exception as e:
            logger.error(f"对话异常: {str(e)}")
            print(f"\n出错了: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
