"""
공통 로깅 유틸리티
모든 Pod에서 사용하는 로깅 설정
"""
import logging
import sys
from typing import Optional
from common.config.base_config import base_config


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 청록색
        'INFO': '\033[32m',     # 녹색
        'WARNING': '\033[33m',  # 노란색
        'ERROR': '\033[31m',    # 빨간색
        'CRITICAL': '\033[35m', # 자주색
        'RESET': '\033[0m'      # 리셋
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """로거 설정"""
    
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 있으면 제거
    if logger.handlers:
        logger.handlers.clear()
    
    # 로그 레벨 설정
    log_level = level or base_config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 핸들러 생성
    handler = logging.StreamHandler(sys.stdout)
    
    # 포매터 설정
    format_str = format_string or base_config.LOG_FORMAT
    if use_colors:
        formatter = ColoredFormatter(format_str)
    else:
        formatter = logging.Formatter(format_str)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 상위 로거로 전파 방지
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """로거 가져오기"""
    return setup_logger(name)


# 기본 로거들
app_logger = get_logger("app")
api_logger = get_logger("api")
db_logger = get_logger("database")
auth_logger = get_logger("auth")