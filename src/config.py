"""Configuration management for SQL Agent."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: str = "openai"  # openai, anthropic, local
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 2000
    streaming: bool = False


@dataclass
class DatabaseConfig:
    """Database configuration."""

    path: str = "data/sample.db"
    type: str = "sqlite"  # sqlite, postgres, mysql
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None


@dataclass
class SafetyConfig:
    """Safety and security configuration."""

    safe_mode: bool = True
    blocked_keywords: list = field(
        default_factory=lambda: [
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "INSERT",
            "UPDATE",
        ]
    )
    allow_read_only: bool = True
    max_query_length: int = 10000


@dataclass
class AgentConfig:
    """Agent behavior configuration."""

    max_iterations: int = 5
    enable_error_correction: bool = True
    enable_tools: bool = True
    memory_size: int = 10  # Number of recent interactions to remember


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    log_file: Optional[str] = "logs/sql_agent.log"
    console_output: bool = True


@dataclass
class Config:
    """Main configuration class."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        config = cls()

        # Load LLM config
        if "llm" in data:
            llm_data = data["llm"]
            config.llm = LLMConfig(
                provider=llm_data.get("provider", "openai"),
                model=llm_data.get("model", "gpt-4o-mini"),
                api_key=llm_data.get("api_key")
                or os.getenv("OPENAI_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY"),
                base_url=llm_data.get("base_url"),
                temperature=llm_data.get("temperature", 0.0),
                max_tokens=llm_data.get("max_tokens", 2000),
                streaming=llm_data.get("streaming", False),
            )

        # Load database config
        if "database" in data:
            db_data = data["database"]
            config.database = DatabaseConfig(
                path=db_data.get("path", "data/sample.db"),
                type=db_data.get("type", "sqlite"),
                host=db_data.get("host"),
                port=db_data.get("port"),
                user=db_data.get("user"),
                password=db_data.get("password"),
                database=db_data.get("database"),
            )

        # Load safety config
        if "safety" in data:
            safety_data = data["safety"]
            config.safety = SafetyConfig(
                safe_mode=safety_data.get("safe_mode", True),
                blocked_keywords=safety_data.get(
                    "blocked_keywords",
                    ["DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "INSERT", "UPDATE"],
                ),
                allow_read_only=safety_data.get("allow_read_only", True),
                max_query_length=safety_data.get("max_query_length", 10000),
            )

        # Load agent config
        if "agent" in data:
            agent_data = data["agent"]
            config.agent = AgentConfig(
                max_iterations=agent_data.get("max_iterations", 5),
                enable_error_correction=agent_data.get("enable_error_correction", True),
                enable_tools=agent_data.get("enable_tools", True),
                memory_size=agent_data.get("memory_size", 10),
            )

        # Load logging config
        if "logging" in data:
            log_data = data["logging"]
            config.logging = LoggingConfig(
                level=log_data.get("level", "INFO"),
                log_file=log_data.get("log_file", "logs/sql_agent.log"),
                console_output=log_data.get("console_output", True),
            )

        return config

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()

        # LLM config from env
        config.llm.provider = os.getenv("LLM_PROVIDER", "openai")
        config.llm.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        config.llm.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        config.llm.base_url = os.getenv("LLM_BASE_URL")
        config.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))
        config.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        config.llm.streaming = os.getenv("LLM_STREAMING", "false").lower() == "true"

        # Database config from env
        config.database.path = os.getenv("DB_PATH", "data/sample.db")
        config.database.type = os.getenv("DB_TYPE", "sqlite")

        return config
