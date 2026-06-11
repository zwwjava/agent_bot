# Changelog

## V0.1.0 - 2026-06-11

- 初始版本发布
- 实现可扩展的 Skill 注册中心架构
- 实现基于 LangChain + LangGraph 的 ReAct Agent
- 接入瑞幸咖啡远程 MCP Server（Streamable HTTP 协议）
- 自动从 SKILL.md 加载业务规则并注入系统提示词
- 支持 MCP 客户端工厂模式，动态连接多个远程 MCP Server
- 实现交互式命令行对话（main.py）
- 统一配置管理（config/settings.py）
- 单例日志管理器（并发安全文件滚动）
- LLM 工厂支持 OpenAI 兼容协议（通义千问、DeepSeek 等）
- 解决 mcp 包命名冲突（项目目录重命名为 mcp_client）