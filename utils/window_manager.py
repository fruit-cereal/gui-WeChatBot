#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
窗口管理模块
处理微信窗口的查找、截图、恢复和最小化等操作
"""

import time
import logging
import numpy as np
import pyautogui
import win32gui
import win32con
import cv2
from config import Config, logger

class WindowManager:
    def __init__(self):
        """初始化窗口管理器"""
        self.wechat_hwnd = None
    
    def find_wechat_window(self):
        """查找微信窗口句柄"""
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if Config.WECHAT_WINDOW_NAME in window_text:
                    hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        
        if hwnds:
            logger.info(f"找到微信窗口，句柄: {hwnds[0]}")
            self.wechat_hwnd = hwnds[0]
            return hwnds[0]
        else:
            logger.error("未找到微信窗口，请确保微信已启动")
            return None
    
    def get_window_rect(self, hwnd=None):
        """获取窗口的位置和大小"""
        if hwnd is None:
            hwnd = self.wechat_hwnd
            
        if hwnd:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                return (left, top, right, bottom)
            except Exception as e:
                logger.error(f"获取窗口位置失败: {e}")
        return None
    
    def restore_window(self, hwnd=None):
        """恢复最小化的窗口"""
        if hwnd is None:
            hwnd = self.wechat_hwnd
            
        if hwnd:
            # 检查窗口是否最小化
            if win32gui.IsIconic(hwnd):
                logger.info("检测到微信窗口已最小化，正在恢复...")
                # 恢复窗口
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)  # 等待窗口恢复
    
    def minimize_window(self, hwnd=None):
        """最小化窗口"""
        if hwnd is None:
            hwnd = self.wechat_hwnd
            
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            logger.debug("已最小化微信窗口")
    
    def is_window_minimized(self, hwnd=None):
        """检查窗口是否最小化"""
        if hwnd is None:
            hwnd = self.wechat_hwnd
            
        if hwnd:
            return win32gui.IsIconic(hwnd)
        return False
    
    def capture_wechat_screen(self):
        """截取微信窗口的屏幕截图"""
        # 查找微信窗口
        if not self.wechat_hwnd:
            self.wechat_hwnd = self.find_wechat_window()
            if not self.wechat_hwnd:
                return None
        
        # 检查窗口是否最小化
        is_minimized = self.is_window_minimized()
        
        # 如果窗口最小化，则不进行截图
        if is_minimized:
            logger.info("微信窗口已最小化，跳过截图")
            return None
        
        # 获取窗口位置
        rect = self.get_window_rect()
        if not rect:
            logger.error("获取窗口位置失败")
            return None
        
        left, top, right, bottom = rect
        width, height = right - left, bottom - top
        
        try:
            # 窗口未最小化，正常截图
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            logger.debug(f"成功截取微信窗口截图，尺寸: {width}x{height}")
            return screenshot
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def click_chat_input(self):
        """点击聊天输入框"""
        if not self.wechat_hwnd:
            logger.error("未找到微信窗口，无法点击聊天输入框")
            return False
        
        try:
            # 获取窗口位置
            rect = self.get_window_rect()
            if not rect:
                return False
            
            left, top, right, bottom = rect
            width, height = right - left, bottom - top
            
            # 恢复窗口（如果最小化）
            self.restore_window()
            
            # 激活窗口
            win32gui.SetForegroundWindow(self.wechat_hwnd)
            time.sleep(1.0)  # 等待窗口激活
            
            # 计算聊天输入框的位置
            chat_x = left + int(width * Config.CHAT_INPUT_BOX_RELATIVE_X)
            chat_y = top + int(height * Config.CHAT_INPUT_BOX_RELATIVE_Y)
            
            # 点击聊天输入框
            logger.info(f"点击聊天输入框位置: ({chat_x}, {chat_y})")
            pyautogui.click(chat_x, chat_y)
            time.sleep(1.0)  # 确保输入框被激活
            
            return True
        except Exception as e:
            logger.error(f"点击聊天输入框失败: {e}")
            return False
