import logging
import os
from pathlib import Path
from config import LOG_CONFIG

#统一配置日志格式和输出文件。
#提供模块级日志记录器。


def setup_logger(name):
    """配置并返回一个logger实例"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG['level'])

    # 创建日志目录如果不存在
    log_dir = os.path.dirname(LOG_CONFIG['file'])
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 创建文件处理器
    file_handler = logging.FileHandler(LOG_CONFIG['file'])
    file_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger