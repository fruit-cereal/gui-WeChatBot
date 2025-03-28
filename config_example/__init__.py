#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块示例
包含应用程序所需的所有配置项和日志设置

【使用说明】
1. 请复制此文件夹为 config 文件夹
2. 修改下面标记为【必须修改】的配置项
3. 根据需要调整其他配置项
"""

from config_example.logger import logger
from config_example.settings import Config

__all__ = ['Config', 'logger']
