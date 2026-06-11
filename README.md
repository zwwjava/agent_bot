# Agent Bot - 智能生活助手

基于 LangChain + LangGraph + MCP 的可扩展智能体框架，一句话触发咖啡下单。

## 项目架构

```
agent_bot/
├── main.py                    # 主入口 - 交互式命令行对话
├── agent.py                   # 智能体构建 + 对话逻辑
├── .env                        # 环境变量配置
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── requirements.txt            # Python 依赖
│
├── config/                     # 配置层
│   ├── __init__.py
│   └── settings.py             # 统一配置（LLM/MCP/Agent等）
│
├── utils/                      # 工具层
│   ├── __init__.py
│   ├── logger.py               # 单例日志管理器（并发安全、文件滚动）
│   └── llms.py                 # LLM 工厂（支持 OpenAI 兼容协议）
│
├── skills/                     # Skill 注册层（易扩展核心）
│   ├── __init__.py             # 统一导入触发注册
│   ├── registry.py             # Skill 注册中心（单例模式）
│   └── coffee/                 # 瑞幸咖啡 Skill
│       ├── __init__.py
│       └── skill.py            # 自动注册 MCP 配置 + SKILL.md 指令
│
├── mcp_client/                 # MCP 客户端层
│   ├── __init__.py
│   └── client.py               # MCP 客户端工厂（单例，自动连接远程 MCP Server）
│
├── prompt/                     # 提示词模板
│   ├── system_prompt_tmpl.md   # 系统提示词（支持 {skill_instructions} 动态注入）
│   └── human_prompt_tmpl.md    # 用户提示词
│
└── doc/my-coffee/              # 原始 Skill 文档（不可修改）
    ├── SKILL.md                 # 瑞幸咖啡下单完整业务规则
    ├── manifest.json
    ├── CHANGELOG.md
    └── LICENSE
```

## 核心设计

### Skill 注册中心模式

每个 Skill 以独立模块注册，提供：
- **MCP 连接配置**：指定远程 MCP Server 的 URL、传输协议、认证头等
- **系统指令**：从 SKILL.md 自动加载业务规则，注入 Agent 系统提示词
- **关键词列表**：用于意图识别和路由

注册流程：
1. 在 `skills/` 下新建目录，编写 `skill.py`
2. 在 `skills/__init__.py` 加一行 `import` 触发自动注册
3. Agent 启动时自动收集所有 Skill 的 MCP 配置和指令

### MCP 远程接入

通过 `langchain-mcp-adapters` 的 `MultiServerMCPClient` 连接瑞幸咖啡远程 MCP Server（Streamable HTTP 协议），自动获取以下工具：

| 工具名 | 功能 |
|--------|------|
| `queryShopList` | 查询瑞幸门店列表 |
| `searchProductForMcp` | 搜索可售商品并匹配 SKU |
| `switchProduct` | 切换商品属性（杯型/温度等） |
| `queryProductDetailInfo` | 查询商品详情 |
| `previewOrder` | 预览订单（获取价格和优惠券） |
| `createOrder` | 创建订单并获取支付二维码 |
| `queryOrderDetailInfo` | 查询订单状态和取餐码 |
| `cancelOrder` | 取消订单 |

### 一句话触发下单

用户输入 → Agent 根据 SKILL.md 业务规则自动执行工具调用链：

```
"帮我点一杯拿铁"
  → queryShopList（查门店）
  → 用户确认门店
  → searchProductForMcp（搜商品）
  → 用户确认下单意图
  → previewOrder（预览价格）
  → createOrder（创建订单 + 支付二维码）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写实际值：

```ini
# LLM 配置（支持任何 OpenAI 兼容协议的模型服务）
LLM_API_KEY=sk-your-actual-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_CHAT_MODEL=qwen-plus-latest

# 瑞幸咖啡 MCP Token（从 https://open.lkcoffee.com/mcp 获取）
LUCKIN_MCP_TOKEN=your-luckin-mcp-token
```

### 3. 运行

```bash
python main.py
```

交互式对话：
```
你: 帮我点一杯拿铁
助手: [自动执行门店查询 → 商品搜索 → 下单流程]
```

## 新增 Skill 示例

以新增"天气查询" Skill 为例：

### 1. 创建 Skill 模块

```bash
mkdir -p skills/weather
```

编写 `skills/weather/skill.py`：

```python
from skills.registry import SkillConfig, registry

def register_weather_skill():
    skill = SkillConfig(
        name="weather",
        description="天气查询助手",
        keywords=["天气", "气温", "下雨", "晴天"],
        mcp_servers={
            "weather-mcp": {
                "url": "http://localhost:8010/mcp",
                "transport": "streamable_http",
            }
        },
        system_instruction="当用户询问天气时，调用天气工具查询并回复。",
    )
    registry.register(skill)

register_weather_skill()
```

### 2. 注册

在 `skills/__init__.py` 添加：

```python
import skills.weather  # noqa: F401
```

完成！Agent 启动时自动连接天气 MCP Server 并加载指令。

## 技术栈

| 技术 | 用途 |
|------|------|
| LangChain | Agent 框架 |
| LangGraph | ReAct Agent + 状态管理 |
| langchain-mcp-adapters | MCP 客户端适配 |
| langchain-openai | OpenAI 兼容 LLM 接入 |
| MCP (Streamable HTTP) | 远程工具调用协议 |