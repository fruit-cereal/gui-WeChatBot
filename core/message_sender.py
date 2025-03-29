#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
消息发送模块
负责将消息发送到微信聊天窗口
"""

import time
import random
import pyperclip
import pyautogui
from config import logger

class MessageSender:
    def __init__(self, window_manager):
        """初始化消息发送器"""
        self.window_manager = window_manager
    
    def send_message(self, message):
        """发送消息到微信聊天框
        
        Args:
            message: 要发送的消息内容
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        try:
            # 首先复制消息到剪贴板
            logger.info(f"复制消息到剪贴板: {message[:30]}...")
            pyperclip.copy(message)
            time.sleep(random.uniform(0.3, 0.8))  # 随机等待复制完成
            
            # 点击聊天输入框
            if not self.window_manager.click_chat_input():
                return False
            time.sleep(random.uniform(0.2, 0.5))  # 随机等待点击完成
            
            # 粘贴消息
            logger.info("粘贴消息")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(random.uniform(0.8, 1.5))  # 随机等待粘贴完成
            
            # 随机决定是否添加额外延迟
            if random.random() < 0.3:  # 30%概率添加额外延迟
                extra_delay = random.uniform(0.2, 0.5)
                logger.info(f"添加额外思考延迟: {extra_delay:.2f}s")
                time.sleep(extra_delay)
            
            # 按下Enter键发送消息
            logger.info("按下Enter键发送消息")
            pyautogui.press('enter')
            time.sleep(random.uniform(0.3, 0.8))  # 随机等待发送完成
            
            logger.info("消息已发送", extra={'save_to_file': True})
            return True
        
        except Exception as e:
            logger.error(f"消息发送失败: {e}", extra={'save_to_file': True})
            return False
