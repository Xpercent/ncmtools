#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
歌单文件排序工具 - 对文件夹中音乐文件按编号重命名或清除编号
"""

import os
import re

MUSIC_EXTENSIONS = ['.mp3', '.flac', '.wav', '.m4a', '.ogg']
SORTED_LIST_FILE = ".sorted_list"


def get_sorted_files(playlist_path):
    """读取已排序文件列表"""
    sorted_list_path = os.path.join(playlist_path, SORTED_LIST_FILE)
    if not os.path.exists(sorted_list_path):
        return []
    
    try:
        with open(sorted_list_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        return []


def save_sorted_files(playlist_path, files):
    """保存已排序文件列表"""
    sorted_list_path = os.path.join(playlist_path, SORTED_LIST_FILE)
    try:
        with open(sorted_list_path, 'w', encoding='utf-8') as f:
            for file in files:
                f.write(file + '\n')
        return True
    except Exception as e:
        print(f"保存排序记录失败: {e}")
        return False


def sort_music_files(playlist_path, end_number):
    """对文件夹中的音乐文件进行编号"""
    sorted_files = get_sorted_files(playlist_path)
    
    # 找出未排序的音乐文件
    music_files = [file for file in os.listdir(playlist_path) 
                  if os.path.isfile(os.path.join(playlist_path, file)) 
                  and os.path.splitext(file)[1].lower() in MUSIC_EXTENSIONS 
                  and file not in sorted_files]
    
    if not music_files:
        print("没有需要重命名的音乐文件")
        return False
    
    print(f"找到 {len(music_files)} 个音乐文件需要重命名")
    renamed_files = []
    rename_count = 0
    
    # 重命名文件
    for i, file in enumerate(music_files):
        current_number = end_number - (len(music_files) - 1 - i)
        old_path = os.path.join(playlist_path, file)
        new_name = f"{current_number}. {file}"
        new_path = os.path.join(playlist_path, new_name)
        
        try:
            os.rename(old_path, new_path)
            print(f"重命名: {current_number}. {file}")
            renamed_files.append(new_name)
            rename_count += 1
        except Exception as e:
            print(f"重命名失败 {file}: {e}")
    
    # 更新排序记录
    if renamed_files:
        save_sorted_files(playlist_path, sorted_files + renamed_files)
        print(f"完成: 重命名 {rename_count} 个文件")
    
    return rename_count > 0


def clear_numbers(playlist_path):
    """清除文件名前的排序编号"""
    sorted_files = get_sorted_files(playlist_path)
    if not sorted_files:
        print("没有排序记录")
        return False
    
    # 找出存在的已排序文件
    existing_files = [file for file in sorted_files 
                     if os.path.isfile(os.path.join(playlist_path, file))]
    
    if not existing_files:
        # 如果没有已排序文件，删除排序记录
        sorted_list_path = os.path.join(playlist_path, SORTED_LIST_FILE)
        if os.path.exists(sorted_list_path):
            os.remove(sorted_list_path)
        print("没有已排序的文件")
        return False
    
    print(f"找到 {len(existing_files)} 个已排序的文件")
    rename_count = 0
    
    # 清除文件编号
    for file in existing_files:
        old_path = os.path.join(playlist_path, file)
        new_name = re.sub(r'^\d+\.\s*', '', file)
        new_path = os.path.join(playlist_path, new_name)
        
        try:
            os.rename(old_path, new_path)
            print(f"清除编号: {file} -> {new_name}")
            rename_count += 1
        except Exception as e:
            print(f"重命名失败 {file}: {e}")
    
    # 如果有文件被处理，删除排序记录
    if rename_count > 0:
        sorted_list_path = os.path.join(playlist_path, SORTED_LIST_FILE)
        if os.path.exists(sorted_list_path):
            os.remove(sorted_list_path)
        
    print(f"完成: 清除 {rename_count} 个文件的编号")
    return True