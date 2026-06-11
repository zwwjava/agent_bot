# Skill 注册中心 - 管理所有 skill 的注册与发现
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from utils.logger import LoggerManager

logger = LoggerManager.get_logger()


@dataclass
class SkillConfig:
    """单个 Skill 的配置信息"""

    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    # MCP 连接配置，格式同 MultiServerMCPClient 的入参
    # 例如: {"my-coffee": {"url": "...", "transport": "streamable_http", "headers": {...}}}
    mcp_servers: dict[str, dict[str, Any]] = field(default_factory=dict)
    # 该 skill 的系统指令（从 SKILL.md 中提取的业务规则）
    system_instruction: str = ""
    # 是否为纯指令型 skill（不提供本地 MCP Server，仅连接远程 MCP）
    instruction_only: bool = False


class SkillRegistry:
    """
    Skill 注册中心 - 全局单例

    使用方式：
      1. 各 skill 模块在导入时调用 register() 注册自己
      2. Agent 启动时通过 get_all_skills() 获取所有已注册 skill
      3. MCP 客户端工厂通过 get_all_mcp_configs() 获取所有 MCP 连接配置
    """

    _instance = None
    _skills: dict[str, SkillConfig] = field(default_factory=dict)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
        return cls._instance

    def register(self, skill: SkillConfig) -> None:
        """注册一个 skill"""
        if skill.name in self._skills:
            logger.warning(f"Skill '{skill.name}' 已注册，将被覆盖")
        self._skills[skill.name] = skill
        logger.info(f"Skill 注册成功: {skill.name} (keywords: {skill.keywords})")

    def unregister(self, name: str) -> None:
        """注销一个 skill"""
        if name in self._skills:
            del self._skills[name]
            logger.info(f"Skill 已注销: {name}")

    def get_skill(self, name: str) -> SkillConfig | None:
        """获取指定 skill"""
        return self._skills.get(name)

    def get_all_skills(self) -> dict[str, SkillConfig]:
        """获取所有已注册 skill"""
        return self._skills.copy()

    def get_all_mcp_configs(self) -> dict[str, dict[str, Any]]:
        """获取所有 skill 的 MCP 连接配置（合并）"""
        configs = {}
        for skill in self._skills.values():
            configs.update(skill.mcp_servers)
        return configs

    def get_all_system_instructions(self) -> str:
        """获取所有 skill 的系统指令（合并拼接）"""
        instructions = []
        for skill in self._skills.values():
            if skill.system_instruction:
                instructions.append(f"## Skill: {skill.name}\n{skill.system_instruction}")
        return "\n\n".join(instructions)

    @property
    def skill_names(self) -> list[str]:
        """所有已注册 skill 名称"""
        return list(self._skills.keys())


# 全局注册中心实例
registry = SkillRegistry()
