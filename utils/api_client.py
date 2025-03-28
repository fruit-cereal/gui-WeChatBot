#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API客户端模块
处理与DeepSeek API的交互
"""

import json
import requests
from config import logger, Config

class APIClient:
    def __init__(self):
        """初始化API客户端"""
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
        
        # 检查API密钥
        if not self.api_key:
            logger.warning("未设置DeepSeek API密钥，请在Config类中设置DEEPSEEK_API_KEY")
    
    def generate_response(self, sender, question, chat_history, current_role):
        """调用DeepSeek API生成回复"""
        if not self.api_key:
            logger.error("未设置DeepSeek API密钥，无法生成回复")
            return "抱歉，我的API密钥未设置，无法回答您的问题。"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 获取当前角色的系统提示词
            system_prompt = Config.get_role_system_prompt(current_role)
            
            # 构建消息列表，包含系统提示和聊天历史
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加聊天历史作为上下文
            for chat in chat_history:
                messages.append({"role": "user", "content": f"{chat['sender']}: {chat['question']}"})
                messages.append({"role": "assistant", "content": chat['response']})
                
            if sender != "未知用户":
                # 添加当前问题
                messages.append({"role": "user", "content": f"{sender}: {question}"})
            else:
                messages.append({"role": "user", "content": f"{question}"})
                
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            logger.info(f"发送API请求，包含{len(chat_history)}轮历史对话")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                logger.info(f"成功生成回复: {answer[:50]}...")
                return answer
            else:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return f"抱歉，API请求失败: {response.status_code}"
        
        except Exception as e:
            logger.error(f"生成回复时出错: {e}")
            return f"抱歉，生成回复时出错: {str(e)}"
