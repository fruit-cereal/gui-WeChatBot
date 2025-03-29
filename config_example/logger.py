#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块
配置日志记录器和自定义过滤器
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 确保日志目录存在
os.makedirs("log", exist_ok=True)

# 自定义日志文件名格式，基于当前日期
def get_log_filename():
    """根据当前日期生成日志文件名"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("log", f"{today}-wechat_bot.log")

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建一个控制台处理器（不过滤，所有信息都输出到控制台）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 创建一个文件处理器（使用过滤器，只记录符合条件的信息）
file_handler = TimedRotatingFileHandler(
    filename=get_log_filename(),  # 使用日期格式化的文件名
    when="midnight",
    interval=1,
    backupCount=30,  # 保留30天的日志
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 阻止日志传递到父logger
logger.propagate = False
