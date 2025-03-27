#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
角色管理工具
提供命令行界面来管理角色配置
"""

import os
import json
import argparse
import sys

def list_roles():
    """列出所有可用角色"""
    roles_dir = os.path.dirname(os.path.abspath(__file__))
    roles = []
    
    print("\n=== 可用角色列表 ===")
    print(f"{'角色名称':<20} {'别名':<30} {'配置文件':<20}")
    print("-" * 70)
    
    for filename in os.listdir(roles_dir):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(roles_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    role_config = json.load(f)
                    
                    if 'name' in role_config and 'aliases' in role_config:
                        print(f"{role_config['name']:<20} {', '.join(role_config['aliases']):<30} {filename:<20}")
                        roles.append(role_config)
            except Exception as e:
                print(f"加载角色配置文件 {filename} 失败: {e}")
    
    print("-" * 70)
    print(f"共找到 {len(roles)} 个角色配置\n")

def add_role():
    """添加新角色"""
    print("\n=== 添加新角色 ===")
    
    # 获取角色信息
    name = input("请输入角色主触发词 (例如: @新角色bot): ")
    if not name:
        print("错误: 角色名称不能为空")
        return
    
    # 获取别名
    aliases_input = input("请输入角色别名，多个别名用逗号分隔 (例如: @新1角色bot,@新l角色bot): ")
    aliases = [alias.strip() for alias in aliases_input.split(',') if alias.strip()]
    
    # 获取系统提示词
    print("\n请输入角色系统提示词 (输入完成后按Ctrl+D结束输入，Windows下按Ctrl+Z然后回车):")
    system_prompt_lines = []
    
    try:
        while True:
            line = input()
            system_prompt_lines.append(line)
    except EOFError:
        pass
    
    system_prompt = "\n".join(system_prompt_lines)
    
    if not system_prompt:
        print("错误: 系统提示词不能为空")
        return
    
    # 生成文件名
    filename = name.replace('@', '').replace(' ', '_').lower()
    if not filename.endswith('.json'):
        filename += '.json'
    
    # 检查文件是否已存在
    roles_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(roles_dir, filename)
    
    if os.path.exists(file_path):
        overwrite = input(f"文件 {filename} 已存在，是否覆盖? (y/n): ")
        if overwrite.lower() != 'y':
            print("操作已取消")
            return
    
    # 创建角色配置
    role_config = {
        "name": name,
        "aliases": aliases,
        "system_prompt": system_prompt
    }
    
    # 保存到文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(role_config, f, ensure_ascii=False, indent=2)
        print(f"\n成功添加角色 {name}，配置已保存到 {filename}")
    except Exception as e:
        print(f"保存角色配置失败: {e}")

def edit_role():
    """编辑现有角色"""
    roles_dir = os.path.dirname(os.path.abspath(__file__))
    role_files = [f for f in os.listdir(roles_dir) if f.endswith('.json')]
    
    if not role_files:
        print("没有找到可编辑的角色配置")
        return
    
    print("\n=== 编辑角色 ===")
    print("可编辑的角色配置:")
    
    for i, filename in enumerate(role_files, 1):
        try:
            with open(os.path.join(roles_dir, filename), 'r', encoding='utf-8') as f:
                role_config = json.load(f)
                print(f"{i}. {role_config.get('name', '未知角色')} ({filename})")
        except:
            print(f"{i}. {filename} (无法读取)")
    
    try:
        choice = int(input("\n请选择要编辑的角色编号: "))
        if choice < 1 or choice > len(role_files):
            print("无效的选择")
            return
        
        filename = role_files[choice - 1]
        file_path = os.path.join(roles_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            role_config = json.load(f)
        
        print(f"\n正在编辑角色: {role_config.get('name', '未知角色')}")
        
        # 编辑角色名称
        new_name = input(f"角色名称 [{role_config.get('name', '')}] (直接回车保持不变): ")
        if new_name:
            role_config['name'] = new_name
        
        # 编辑别名
        current_aliases = ', '.join(role_config.get('aliases', []))
        new_aliases = input(f"别名 [{current_aliases}] (直接回车保持不变): ")
        if new_aliases:
            role_config['aliases'] = [alias.strip() for alias in new_aliases.split(',') if alias.strip()]
        
        # 编辑系统提示词
        print(f"\n当前系统提示词:")
        print(role_config.get('system_prompt', ''))
        
        edit_prompt = input("\n是否编辑系统提示词? (y/n): ")
        if edit_prompt.lower() == 'y':
            print("\n请输入新的系统提示词 (输入完成后按Ctrl+D结束输入，Windows下按Ctrl+Z然后回车):")
            system_prompt_lines = []
            
            try:
                while True:
                    line = input()
                    system_prompt_lines.append(line)
            except EOFError:
                pass
            
            new_system_prompt = "\n".join(system_prompt_lines)
            if new_system_prompt:
                role_config['system_prompt'] = new_system_prompt
        
        # 保存修改
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(role_config, f, ensure_ascii=False, indent=2)
        
        print(f"\n成功更新角色 {role_config['name']}，配置已保存到 {filename}")
        
    except ValueError:
        print("请输入有效的数字")
    except Exception as e:
        print(f"编辑角色失败: {e}")

def delete_role():
    """删除角色"""
    roles_dir = os.path.dirname(os.path.abspath(__file__))
    role_files = [f for f in os.listdir(roles_dir) if f.endswith('.json')]
    
    if not role_files:
        print("没有找到可删除的角色配置")
        return
    
    print("\n=== 删除角色 ===")
    print("可删除的角色配置:")
    
    for i, filename in enumerate(role_files, 1):
        try:
            with open(os.path.join(roles_dir, filename), 'r', encoding='utf-8') as f:
                role_config = json.load(f)
                print(f"{i}. {role_config.get('name', '未知角色')} ({filename})")
        except:
            print(f"{i}. {filename} (无法读取)")
    
    try:
        choice = int(input("\n请选择要删除的角色编号 (0取消): "))
        if choice == 0:
            print("操作已取消")
            return
        
        if choice < 1 or choice > len(role_files):
            print("无效的选择")
            return
        
        filename = role_files[choice - 1]
        file_path = os.path.join(roles_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                role_config = json.load(f)
                role_name = role_config.get('name', '未知角色')
        except:
            role_name = filename
        
        confirm = input(f"确定要删除角色 {role_name}? (y/n): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        os.remove(file_path)
        print(f"\n成功删除角色 {role_name}")
        
    except ValueError:
        print("请输入有效的数字")
    except Exception as e:
        print(f"删除角色失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='角色管理工具')
    parser.add_argument('action', choices=['list', 'add', 'edit', 'delete'], 
                        help='要执行的操作: list (列出所有角色), add (添加新角色), edit (编辑角色), delete (删除角色)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_roles()
    elif args.action == 'add':
        add_role()
    elif args.action == 'edit':
        edit_role()
    elif args.action == 'delete':
        delete_role()

if __name__ == "__main__":
    main()
