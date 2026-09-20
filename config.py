"""
Configuration management for the LiveKit Friday agent.
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class HomeAssistantConfig:
    """Home Assistant configuration settings."""
    url: str
    token: str
    mcp_url: Optional[str] = None
    mcp_token: Optional[str] = None
    mcp_retry_attempts: int = 3
    mcp_timeout: int = 30

    @classmethod
    def from_env(cls) -> Optional['HomeAssistantConfig']:
        """Create config from environment variables."""
        url = os.getenv("HA_URL", "http://homeassistant.local:8123")
        token = os.getenv("HA_TOKEN")
        # MCP-specific variables
        mcp_url = os.getenv("HOME_ASSISTANT_MCP_URL")
        mcp_token = os.getenv("HOME_ASSISTANT_TOKEN")
        if not token:
            return None
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        return cls(
            url=url,
            token=token,
            mcp_url=mcp_url,
            mcp_token=mcp_token,
            mcp_retry_attempts=int(os.getenv("HA_MCP_RETRY_ATTEMPTS", "3")),
            mcp_timeout=int(os.getenv("HA_MCP_TIMEOUT", "30"))
        )

@dataclass
class AgentConfig:
    """Agent configuration settings."""
    name: str = "Friday"
    voice: str = "default"  # Using default voice for Gemini 2.0 Flash Live
    temperature: float = 0.7
    max_response_length: int = 1000
    enable_video: bool = False
    enable_noise_cancellation: bool = True
    # Wake word configuration
    enable_wake_word: bool = True
    wake_words: list = None
    wakeword_backend: str = "openwakeword"
    wake_word_activation_delay: float = 0.5

    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ["hey_assistant", "computer", "friday"]

    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create config from environment variables."""
        wake_words_str = os.getenv("AGENT_WAKE_WORDS", "hey_assistant,computer,friday")
        wake_words = [w.strip() for w in wake_words_str.split(",") if w.strip()]
        
        return cls(
            name=os.getenv("AGENT_NAME", "Friday"),
            voice=os.getenv("AGENT_VOICE", "default"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
            max_response_length=int(os.getenv("AGENT_MAX_RESPONSE_LENGTH", "1000")),
            enable_video=os.getenv("AGENT_ENABLE_VIDEO", "false").lower() == "true",
            enable_noise_cancellation=os.getenv("AGENT_ENABLE_NOISE_CANCELLATION", "true").lower() == "true",
            enable_wake_word=os.getenv("AGENT_ENABLE_WAKE_WORD", "true").lower() == "true",
            wake_words=wake_words,
            wakeword_backend=os.getenv("AGENT_WAKEWORD_BACKEND", "openwakeword"),
            wake_word_activation_delay=float(os.getenv("AGENT_WAKE_WORD_DELAY", "0.5"))
        )

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "logs/agent.log"

    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create config from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE_PATH", "logs/agent.log")
        )

@dataclass
class AppConfig:
    """Main application configuration."""
    home_assistant: Optional[HomeAssistantConfig]
    agent: AgentConfig
    logging: LoggingConfig

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create complete config from environment variables."""
        return cls(
            home_assistant=HomeAssistantConfig.from_env(),
            agent=AgentConfig.from_env(),
            logging=LoggingConfig.from_env()
        )

# Global config instance
config = AppConfig.from_env()

# Load configuration from environment variables
def load_config() -> AppConfig:
    config = AppConfig.from_env()

    # Agent configuration
    config.agent.name = os.getenv("AGENT_NAME", config.agent.name)
    config.agent.voice = os.getenv("AGENT_VOICE", config.agent.voice)
    config.agent.temperature = float(os.getenv("AGENT_TEMPERATURE", config.agent.temperature))
    config.agent.max_response_length = int(os.getenv("AGENT_MAX_RESPONSE_LENGTH", config.agent.max_response_length))
    config.agent.enable_video = os.getenv("AGENT_ENABLE_VIDEO", "false").lower() == "true"
    config.agent.enable_noise_cancellation = os.getenv("AGENT_ENABLE_NOISE_CANCELLATION", "true").lower() == "true"
    config.agent.enable_wake_word = os.getenv("AGENT_ENABLE_WAKE_WORD", "true").lower() == "true"
    wake_words_str = os.getenv("AGENT_WAKE_WORDS", "hey_assistant,computer,friday")
    config.agent.wake_words = [w.strip() for w in wake_words_str.split(",") if w.strip()]
    config.agent.wakeword_backend = os.getenv("AGENT_WAKEWORD_BACKEND", "openwakeword")
    config.agent.wake_word_activation_delay = float(os.getenv("AGENT_WAKE_WORD_DELAY", "0.5"))

    # Logging configuration
    config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
    config.logging.format = os.getenv("LOG_FORMAT", config.logging.format)
    config.logging.file_path = os.getenv("LOG_FILE_PATH", config.logging.file_path)

    return config

config = load_config()
