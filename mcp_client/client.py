# MCP 客户端工厂 - 根据已注册的 skill 自动创建 MCP 客户端并获取工具
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

from skills.registry import registry
from utils.logger import LoggerManager

logger = LoggerManager.get_logger()

class MCPClientFactory:
    """
    MCP 客户端工厂

    根据已注册 skill 的 MCP 配置，自动创建 MultiServerMCPClient，
    并获取所有远程 MCP Server 提供的工具列表。
    """

    _instance = None
    _client: MultiServerMCPClient | None = None
    _tools: list[BaseTool] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> list[BaseTool]:
        """
        初始化 MCP 客户端，连接所有已注册的 MCP Server，获取工具列表

        Returns:
            list[BaseTool]: 所有 MCP 工具列表
        """
        mcp_configs = registry.get_all_mcp_configs()

        if not mcp_configs:
            logger.warning("没有已注册的 MCP 配置，将不使用任何 MCP 工具")
            return []

        logger.info(f"正在连接 MCP 服务器: {list(mcp_configs.keys())}")

        try:
            self._client = MultiServerMCPClient(mcp_configs)
            self._tools = await self._client.get_tools()

            tool_names = [t.name for t in self._tools]
            logger.info(f"MCP 工具获取成功，共 {len(self._tools)} 个: {tool_names}")

            return self._tools

        except Exception as e:
            logger.error(f"MCP 客户端初始化失败: {str(e)}")
            raise

    @property
    def tools(self) -> list[BaseTool]:
        """获取已加载的 MCP 工具列表"""
        return self._tools

    @property
    def client(self) -> MultiServerMCPClient | None:
        """获取 MCP 客户端实例"""
        return self._client


# 全局工厂实例
mcp_factory = MCPClientFactory()
