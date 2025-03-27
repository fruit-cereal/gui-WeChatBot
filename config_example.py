#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信机器人配置文件示例
包含所有配置参数和角色设定
实际使用时请复制此文件为 config.py 并填入自己的配置
"""

import logging
import os
from roles import load_all_roles

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wechat_bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    # 从roles目录加载所有角色配置
    ROLES = load_all_roles()
    
    # 默认角色（初始化时使用）
    DEFAULT_ROLE = "@专业助手bot"
    
    # 截图和OCR相关
    SCREENSHOT_INTERVAL = 5  # 截图间隔（秒）
    OCR_CONFIDENCE_THRESHOLD = 0.6  # OCR识别置信度阈值
    
    # DeepSeek API配置
    # 从环境变量读取API密钥，提高安全性
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        # 如果环境变量未设置，记录错误并可能引发异常或退出
        error_message = "错误：环境变量 DEEPSEEK_API_KEY 未设置。请设置该环境变量以使用DeepSeek API。"
        logger.error(error_message)
        raise ValueError(error_message) 

        
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 微信窗口相关
    WECHAT_WINDOW_NAME = "你的微信窗口名称"  # 微信窗口标题（请修改为自己的）
    WECHAT_WINDOW_NAME_ALIASES = ["微信窗口别名1", "微信窗口别名2"]  # 微信窗口标题的可能OCR识别变体
    
    # 聊天框和发送按钮的相对位置（需要根据实际情况调整）
    # 这些值是相对于窗口的百分比位置
    CHAT_INPUT_BOX_RELATIVE_X = 0.5  # 聊天输入框的X坐标（窗口宽度的百分比）
    CHAT_INPUT_BOX_RELATIVE_Y = 0.88  # 聊天输入框的Y坐标（窗口高度的百分比）
    SEND_BUTTON_RELATIVE_X = 0.95  # 发送按钮的X坐标（窗口宽度的百分比）
    SEND_BUTTON_RELATIVE_Y = 0.85  # 发送按钮的Y坐标（窗口高度的百分比）
    
    # 聊天历史相关
    CHAT_HISTORY_DIR = "chat_histories"
    MAX_HISTORY_LENGTH = 20  # 内存中保存的最大对话轮数
    MAX_API_HISTORY_LENGTH = 10  # 发送给API的最大对话轮数
    DUPLICATE_CHECK_HISTORY_LENGTH = 5  # 检查重复问题时往前查找的对话轮数，设为0表示禁用重复检查
    
    @classmethod
    def get_role_system_prompt(cls, role):
        """根据角色获取对应的系统提示词"""
        # 默认的系统提示词
        default_prompt = """
        你是一个微信机器人，要扮演一个特定角色在微信中回复他人
        【角色设定】
        - 友好、专业的助手
        - 回答简洁明了，有礼貌
        - 尽量提供有用的信息

        【强制规则】
        1. 回答简短，避免过长的回复
        2. 使用礼貌的语气
        3. 如果不确定，坦诚表示不知道
        """
        
        # 从ROLES列表中查找匹配的角色
        for role_config in cls.ROLES:
            if role_config["name"] in role or any(alias in role for alias in role_config["aliases"]):
                return role_config["system_prompt"]
        
        # 对于未知角色，使用默认提示词
        return default_prompt

# 确保聊天历史目录存在
os.makedirs(Config.CHAT_HISTORY_DIR, exist_ok=True)
