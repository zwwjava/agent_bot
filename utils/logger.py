# 日志管理模块 - 单例模式，支持并发安全文件滚动
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from config.settings import Config


class LoggerManager:
    """日志管理器 - 全局单例"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []

        handler = ConcurrentRotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.MAX_BYTES,
            backupCount=Config.BACKUP_COUNT,
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self._logger.addHandler(handler)

        # 同时输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self._logger.addHandler(console_handler)

    @property
    def logger(self):
        return self._logger

    @classmethod
    def get_logger(cls):
        instance = cls()
        return instance.logger
