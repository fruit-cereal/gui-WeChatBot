#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置模块
配置日志记录器和自定义过滤器
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta # 导入timedelta

# 确保日志目录存在
os.makedirs("log", exist_ok=True)

# --- 自定义轮转日志文件名 ---
def daily_log_namer(default_name):
    """在轮转时生成 YYYY-MM-DD-wechat_bot.log 格式的文件名"""
    # default_name 格式通常是 filename.YYYY-MM-DD 或 filename.YYYY-MM-DD_HH-MM-SS
    # 我们需要提取日期部分
    base_filename, date_str = os.path.splitext(default_name)
    # 如果有时间戳，去掉时间戳部分
    date_part = date_str.split('_')[0].strip('.') # .YYYY-MM-DD
    
    # TimedRotatingFileHandler 在午夜轮转时，使用的是 *前一天* 的日期来命名备份文件
    # 所以我们直接使用提取出的日期
    log_date_str = date_part 
    
    # 构建新的文件名
    # 注意：原 base_filename 是 log/wechat_bot_current.log，我们需要的是 log/YYYY-MM-DD-wechat_bot.log
    log_dir = os.path.dirname(base_filename) # 获取 log 目录
    return os.path.join(log_dir, f"{log_date_str}-wechat_bot.log")

# --- 自定义过滤器 ---
class FileLogFilter(logging.Filter):
    """
    自定义日志过滤器，只允许带有 'save_to_file' 标记的记录通过。
    """
    def filter(self, record):
        # 检查记录是否有名为 'save_to_file' 的属性，并且其值为 True
        # 如果没有这个属性，默认为 False (即不保存到文件)
        return getattr(record, 'save_to_file', False)

# --- Logger 设置 ---
logger = logging.getLogger("WeChatBotLogger") # 给logger一个名字
# 设置全局最低日志级别为 INFO (不再依赖Config)
logger.setLevel(logging.INFO)


# --- 格式化器 ---
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # 添加了logger名字

# --- 控制台处理器 ---
# 控制台始终显示INFO及以上级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
# 控制台处理器不过滤，显示所有达到其级别的日志
logger.addHandler(console_handler)


# --- 文件处理器 ---
# 文件处理器也使用INFO级别，但会通过过滤器筛选
# 注意：filename 现在是固定的，namer 用于生成轮转后的文件名
file_handler = TimedRotatingFileHandler(
    filename=os.path.join("log", "wechat_bot_current.log"), # 固定当前日志文件名
    when="midnight",
    interval=1,
    backupCount=30, # 保留最近30天的日志
    encoding='utf-8',
    namer=daily_log_namer # 使用自定义命名函数
)
file_handler.setLevel(logging.INFO) # 与logger级别一致
file_handler.setFormatter(formatter)

# --- 添加过滤器到文件处理器 ---
file_filter = FileLogFilter()
file_handler.addFilter(file_filter) # 只给文件处理器添加过滤器

# --- 添加文件处理器到Logger ---
logger.addHandler(file_handler)


# --- 防止日志向上传播 ---
# 如果根logger有处理器，可能会导致日志重复打印
logger.propagate = False
