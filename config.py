#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信机器人配置文件
包含所有配置参数和角色设定
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
    DEEPSEEK_API_KEY = "sk-96631c20650f46ae80015183d99e5529"  # 需要填入你的DeepSeek API密钥
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 微信窗口相关
    WECHAT_WINDOW_NAME = "潘圣伟大"  # 微信窗口标题（可能需要调整）
    
    # 聊天框和发送按钮的相对位置（需要根据实际情况调整）
    # 这些值是相对于窗口的百分比位置
    CHAT_INPUT_BOX_RELATIVE_X = 0.5  # 聊天输入框的X坐标（窗口宽度的百分比）
    CHAT_INPUT_BOX_RELATIVE_Y = 0.85  # 聊天输入框的Y坐标（窗口高度的百分比）- 调高了位置
    SEND_BUTTON_RELATIVE_X = 0.95  # 发送按钮的X坐标（窗口宽度的百分比）
    SEND_BUTTON_RELATIVE_Y = 0.85  # 发送按钮的Y坐标（窗口高度的百分比）- 同样调高
    
    # 聊天历史相关
    CHAT_HISTORY_DIR = "chat_histories"
    MAX_HISTORY_LENGTH = 20  # 内存中保存的最大对话轮数
    MAX_API_HISTORY_LENGTH = 10  # 发送给API的最大对话轮数
    DUPLICATE_CHECK_HISTORY_LENGTH = 5  # 检查重复问题时往前查找的对话轮数
    
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
