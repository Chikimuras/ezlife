import sys
from pathlib import Path

from loguru import logger


class LoggerConfig:
    @staticmethod
    def setup():
        logger.remove()

        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

        logger.add(
            Path("logs") / "app_{time:YYYY-MM-DD}.log",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{name}:{function}:{line} | {message}"
            ),
            level="INFO",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

        logger.add(
            Path("logs") / "error_{time:YYYY-MM-DD}.log",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{name}:{function}:{line} | {message}\n{exception}"
            ),
            level="ERROR",
            rotation="00:00",
            retention="90 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

        logger.info("🚀 Loguru logging configured successfully")


def get_logger(name: str):
    return logger.bind(name=name)
