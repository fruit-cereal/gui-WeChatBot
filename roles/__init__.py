#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
角色配置模块
包含所有角色的配置信息
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

def load_all_roles():
    """加载所有角色配置"""
    roles_dir = os.path.dirname(os.path.abspath(__file__))
    roles = []
    
    # 遍历roles目录下的所有json文件
    for filename in os.listdir(roles_dir):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(roles_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    role_config = json.load(f)
                    
                    # 验证角色配置是否有效
                    if 'name' in role_config and 'aliases' in role_config and 'system_prompt' in role_config:
                        roles.append(role_config)
                        logger.info(f"已加载角色配置: {role_config['name']}")
                    else:
                        logger.warning(f"角色配置文件 {filename} 格式无效，已跳过")
            except Exception as e:
                logger.error(f"加载角色配置文件 {filename} 失败: {e}")
    
    return roles
