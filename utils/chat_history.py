#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天历史管理模块
处理聊天历史记录的加载、保存和管理
"""

import os
import re
import json
from datetime import datetime
from config import logger, Config

class ChatHistoryManager:
    def __init__(self):
        """初始化聊天历史管理器"""
        # 存储聊天记录作为上下文，本地保存无限轮对话，但API只发送最近20轮
        self.chat_history = []
        self.max_history_length = Config.MAX_HISTORY_LENGTH  # 内存中保存的最大对话轮数
        self.max_api_history_length = Config.MAX_API_HISTORY_LENGTH  # 发送给API的最大对话轮数
        
        # 创建对话历史文件目录
        self.chat_history_dir = Config.CHAT_HISTORY_DIR
        os.makedirs(self.chat_history_dir, exist_ok=True)
        
        # 当前角色和对话历史文件路径
        self.current_role = Config.DEFAULT_ROLE
        self.chat_history_file = self.get_history_file_path(self.current_role)
        
        logger.info(f"当前角色: {self.current_role}")
        logger.info(f"对话历史文件: {self.chat_history_file}")
        
        # 加载历史对话记录
        self.load_chat_history()
    
    def get_history_file_path(self, role):
        """根据角色名称生成对话历史文件路径"""
        # 将角色名称转换为有效的文件名
        # 移除特殊字符，只保留字母、数字、下划线
        valid_filename = re.sub(r'[^\w\s]', '', role)
        valid_filename = valid_filename.replace(' ', '_')
        
        # 如果文件名为空，使用默认名称
        if not valid_filename:
            valid_filename = "default_role"
        
        return os.path.join(self.chat_history_dir, f"{valid_filename}_history.json")
    
    def switch_role(self, new_role):
        """切换到新角色，保存当前对话历史并加载新角色的对话历史"""
        if new_role == self.current_role:
            return  # 如果角色相同，不需要切换
        
        logger.info(f"检测到角色变更: {self.current_role} -> {new_role}")
        
        # 保存当前角色的对话历史
        self.save_chat_history()
        
        # 更新当前角色和对话历史文件路径
        self.current_role = new_role
        self.chat_history_file = self.get_history_file_path(self.current_role)
        
        logger.info(f"切换到新角色: {self.current_role}")
        logger.info(f"新对话历史文件: {self.chat_history_file}")
        
        # 加载新角色的对话历史
        self.load_chat_history()
    
    def load_chat_history(self):
        """从本地文件加载历史对话记录"""
        try:
            if os.path.exists(self.chat_history_file):
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
                logger.info(f"成功从{self.chat_history_file}加载了{len(self.chat_history)}轮历史对话")
                
                # 如果内存中的历史记录超过最大长度，只保留最新的部分
                if len(self.chat_history) > self.max_history_length:
                    self.chat_history = self.chat_history[-self.max_history_length:]
                    logger.info(f"历史对话超过最大长度，只保留最新的{self.max_history_length}轮对话")
            else:
                logger.info(f"未找到角色'{self.current_role}'的历史对话文件，将创建新的对话历史")
                self.chat_history = []
        except Exception as e:
            logger.error(f"加载历史对话失败: {e}")
            self.chat_history = []
    
    def save_chat_history(self):
        """将对话历史保存到本地文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.chat_history_file), exist_ok=True)
            
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            logger.info(f"成功将{len(self.chat_history)}轮对话历史保存到{self.chat_history_file}")
        except Exception as e:
            logger.error(f"保存对话历史失败: {e}")
    
    def add_chat(self, sender, question, response):
        """添加新的对话记录"""
        # 创建新的对话记录，包含时间戳
        new_chat = {
            'sender': sender,
            'question': question,
            'response': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'role': self.current_role  # 记录当前角色
        }
        
        # 将当前对话添加到历史记录
        self.chat_history.append(new_chat)
        
        # 如果内存中的历史记录超过最大长度，删除最早的对话
        if len(self.chat_history) > self.max_history_length:
            removed = self.chat_history.pop(0)
            logger.info(f"内存中历史记录已达到最大长度，删除最早的对话: {removed['sender']}: {removed['question'][:20]}...")
        
        # 保存对话历史到本地文件
        self.save_chat_history()
    
    def get_recent_history(self):
        """获取最近的对话历史（用于API请求）"""
        # 只返回最近的几轮对话作为上下文
        return self.chat_history[-self.max_api_history_length:] if len(self.chat_history) > self.max_api_history_length else self.chat_history
    
    def is_similar_question(self, question1, question2):
        """判断两个问题是否相似（简单实现）"""
        # 去除标点符号和空格，转为小写进行比较
        def normalize(text):
            # 去除常见标点符号和空格
            for char in "，。！？、；：""''（）【】《》「」『』〈〉…—～,.!?;:\"'()[]<>":
                text = text.replace(char, "")
            return text.lower().strip()
        
        q1 = normalize(question1)
        q2 = normalize(question2)
        
        # 如果两个问题完全相同
        if q1 == q2:
            return True
        
        # 如果一个问题是另一个问题的子串
        if q1 in q2 or q2 in q1:
            return True
        
        # 计算简单的相似度（共同字符数 / 较长字符串长度）
        common_chars = set(q1) & set(q2)
        similarity = len(common_chars) / max(len(set(q1)), len(set(q2)))
        
        # 如果相似度超过阈值，认为是相似问题
        return similarity > 0.8
    
    def is_question_already_answered(self, question, sender=None):
        """检查问题是否在历史记录中已经出现过
        
        Args:
            question: 要检查的问题
            sender: 问题的发送者，如果为None则忽略发送者检查
            
        Returns:
            bool: 如果同一发送者的相似问题已存在则返回True，否则返回False
        """
        # 如果DUPLICATE_CHECK_HISTORY_LENGTH为0，表示不进行重复检查
        if Config.DUPLICATE_CHECK_HISTORY_LENGTH <= 0:
            return False
            
        # 只检查最近的几轮对话，数量由配置文件中的DUPLICATE_CHECK_HISTORY_LENGTH决定
        check_length = min(Config.DUPLICATE_CHECK_HISTORY_LENGTH, len(self.chat_history))
        recent_chats = self.chat_history[-check_length:]
        
        for chat in recent_chats:
            # 使用简单的相似度检查，如果问题相似度超过80%，则认为是相同问题
            if self.is_similar_question(question, chat['question']):
                # 如果提供了发送者，需要检查发送者和角色是否都相同
                if sender is not None:
                    # 检查发送者和角色是否都相同
                    if chat['sender'] == sender and chat['role'] == self.current_role:
                        logger.info(f"用户'{sender}'向角色'{self.current_role}'提出的问题'{question}'与其最近{check_length}轮对话中的问题'{chat['question']}'相似")
                        return True
                    else:
                        # 即使问题相似，但如果发送者或角色不同，则不视为重复
                        if chat['sender'] != sender:
                            logger.info(f"问题'{question}'虽与历史中的'{chat['question']}'相似，但发送者不同（当前：{sender}，历史：{chat['sender']}），允许回答")
                        elif chat['role'] != self.current_role:
                            logger.info(f"问题'{question}'虽与历史中的'{chat['question']}'相似，但角色不同（当前：{self.current_role}，历史：{chat['role']}），允许回答")
                        continue # 继续检查下一条历史记录
                else:
                    # 如果没有提供发送者，保持原有行为（只检查问题相似性）
                    logger.info(f"问题'{question}'与最近{check_length}轮对话中的问题'{chat['question']}'相似")
                    return True
        
        return False
