#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信群聊机器人
通过屏幕截图和OCR识别来监控微信群聊，当检测到有人@机器人时自动回复。
注意：仅在微信窗口未最小化时工作。
"""

from core.bot import WeChatBot

if __name__ == "__main__":
    # 创建并运行微信机器人
    bot = WeChatBot()
    bot.run()
