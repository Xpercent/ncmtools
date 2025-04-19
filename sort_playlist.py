#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import difflib

# 支持的音频文件格式改为集合，提高成员检查速度
AUDIO_EXTENSIONS = {'.mp3', '.flac', '.wav', '.ogg'}

# 缓存正则表达式
NUMBER_PREFIX_PATTERN = re.compile(r'^\d+\.\s')

def get_playlists(base_dir):
    """获取所有可用的歌单目录"""
    playlists = []
    try:
        # 使用os.scandir替代os.listdir提高性能
        for entry in os.scandir(base_dir):
            if entry.is_dir():
                playlists.append(entry.name)
        return playlists
    except Exception as e:
        print(f"读取歌单目录时出错: {e}")
        return []

def select_playlist(playlists):
    """让用户选择一个歌单"""
    if not playlists:
        print("没有找到可用的歌单！")
        return None
    
    print("可用的歌单:")
    for i, playlist in enumerate(playlists, 1):
        print(f"{i}. {playlist}")
    
    while True:
        try:
            choice = int(input("请输入歌单编号: "))
            if 1 <= choice <= len(playlists):
                return playlists[choice - 1]
            else:
                print(f"请输入1-{len(playlists)}之间的数字")
        except ValueError:
            print("请输入有效的数字")

def get_final_number():
    """获取用户指定的末尾编号"""
    while True:
        try:
            num = int(input("请输入末尾编号（歌单最后一首歌的编号）: "))
            if num > 0:
                return num
            else:
                print("请输入大于0的数字")
        except ValueError:
            print("请输入有效的数字")

def read_playlist_json(playlist_dir):
    """读取歌单JSON文件，提取歌曲信息"""
    if not os.path.exists(playlist_dir):
        print(f"错误: 未找到歌单JSON文件 {playlist_dir}")
        return None
    try:
        with open(playlist_dir, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"读取JSON文件时出错: {e}")
        return None

def get_audio_files(playlist_dir):
    """获取目录中的所有音频文件，返回字典{文件名无扩展名: 扩展名}"""
    audio_files_map = {}
    for entry in os.scandir(playlist_dir):
        if entry.is_file():
            file = entry.name
            # 优化扩展名检查
            _, ext = os.path.splitext(file.lower())
            if ext in AUDIO_EXTENSIONS:
                # 键为不含扩展名的文件名，值为扩展名
                name, ext = os.path.splitext(file)
                audio_files_map[name] = ext
    return audio_files_map

def find_best_match(title, audio_files_map):
    """使用模糊匹配找到最匹配的音频文件"""
    if not audio_files_map:
        return None
    # 使用difflib找到最佳匹配
    matches = difflib.get_close_matches(title, audio_files_map.keys(), n=1, cutoff=0.6)
    if matches:
        best_match = matches[0]
        # 返回匹配的文件名和扩展名
        return best_match, audio_files_map.get(best_match)
            
    return None

def is_already_sorted(filename):
    """检查文件名是否已经有序号前缀"""
    return bool(NUMBER_PREFIX_PATTERN.match(filename))

def remove_number_prefix(filename):
    """移除文件名中的编号前缀"""
    return NUMBER_PREFIX_PATTERN.sub('', filename)

def rename_audio_files(playlist_dir, tracks, start_number):
    """重命名音频文件，添加序号前缀"""
    audio_files_map = get_audio_files(playlist_dir)
    sorted_file = os.path.join(playlist_dir, ".sorted")
    already_sorted = []
    
    # 读取已排序文件
    if os.path.exists(sorted_file):
        try:
            with open(sorted_file, 'r', encoding='utf-8') as f:
                already_sorted = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"读取.sorted文件时出错: {e}")
    
    # 逆序处理tracks
    current_number = start_number
    processed_count = 0
    not_found_count = 0
    not_found_tracks = []
    renamed_files = []
    # 收集所有需要重命名的文件
    rename_operations = []
    
    print(f"\n开始处理歌单，共 {len(tracks)} 首歌曲")

    for track in reversed(tracks):
        title = track.get('full_title', '')
        if not title:
            continue
        matched_result = find_best_match(title, audio_files_map)
        
        if matched_result:
            matched_name, matched_ext = matched_result
            
            current_file = matched_name + matched_ext  # 当前的文件名
            file_path = os.path.join(playlist_dir, current_file)
            
            # 获取不含编号的文件名
            original_filename = f"{title}{matched_ext}"  # 原始的文件名，json中的
            
            # 从audio_files_map中删除已匹配的文件，避免重复匹配
            if matched_name in audio_files_map:
                del audio_files_map[matched_name]
            
            # 新文件名
            new_name = f"{current_number}. {original_filename}"
            new_path = os.path.join(playlist_dir, new_name)
            
            # 如果文件名没有变化，则跳过
            if current_file == new_name:
                renamed_files.append(new_name)
                current_number -= 1
                continue
                
            # 收集重命名操作而不是立即执行
            rename_operations.append((file_path, new_path, current_file, new_name))
            renamed_files.append(new_name)
            
            # 处理对应的.lrc文件
            lrc_file = os.path.join(playlist_dir, f"{matched_name}.lrc")
            if os.path.exists(lrc_file):
                new_lrc_name = f"{current_number}. {title}.lrc"
                new_lrc_path = os.path.join(playlist_dir, new_lrc_name)
                try:
                    os.rename(lrc_file, new_lrc_path)
                    print(f"成功重命名歌词文件: {matched_name}.lrc -> {new_lrc_name}")
                except Exception as e:
                    print(f"重命名歌词文件时出错: {e}")
        else:
            print(f"未找到匹配的文件: {title}")
            not_found_count += 1
            not_found_tracks.append(title)
            
        current_number -= 1
    
    # 批量执行重命名操作
    for file_path, new_path, current_file, new_name in rename_operations:
        try:
            os.rename(file_path, new_path)
            print(f"成功重命名: {current_file} -> {new_name}")
            processed_count += 1
        except Exception as e:
            print(f"重命名文件时出错: {e}")
    
    # 只有在有成功重命名的文件时才更新.sorted文件
    if renamed_files:
        try:
            with open(sorted_file, 'w', encoding='utf-8') as f:
                for name in renamed_files:
                    f.write(name + '\n')
        except Exception as e:
            print(f"更新.sorted文件时出错: {e}")
    
    # 输出摘要
    print("\n处理完成！")
    print(f"共处理: {processed_count} 首歌曲")
    print(f"未找到: {not_found_count} 首歌曲")
    
def remove_numbers(playlist_dir):
    """移除所有歌曲文件名中的编号前缀，包括对应的歌词文件"""
    sorted_file = os.path.join(playlist_dir, ".sorted")
    sorted_files = []
    
    # 检查.sorted文件是否存在
    if not os.path.exists(sorted_file):
        print("错误: 未找到.sorted文件，无法确定哪些文件已排序")
        return
    
    # 读取.sorted文件
    try:
        with open(sorted_file, 'r', encoding='utf-8') as f:
            sorted_files = [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"读取.sorted文件时出错: {e}")
        return
    
    if not sorted_files:
        print("没有找到已排序的文件")
        return
    
    print(f"\n开始移除编号，共 {len(sorted_files)} 个文件")
    processed_count = 0
    rename_operations = []
    
    for file in sorted_files:
        file_path = os.path.join(playlist_dir, file)
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file}")
            continue
        
        if not is_already_sorted(file):
            print(f"文件没有编号: {file}")
            continue
        
        # 移除编号前缀
        new_name = remove_number_prefix(file)
        new_path = os.path.join(playlist_dir, new_name)
        
        # 收集重命名操作
        rename_operations.append((file_path, new_path, file, new_name))

        # 处理对应的.lrc文件
        lrc_file = os.path.join(playlist_dir, f"{os.path.splitext(file)[0]}.lrc")
        if os.path.exists(lrc_file):
            new_lrc_name = remove_number_prefix(f"{os.path.splitext(new_name)[0]}.lrc")
            new_lrc_path = os.path.join(playlist_dir, new_lrc_name)
            rename_operations.append((lrc_file, new_lrc_path, lrc_file, new_lrc_name))
    
    # 批量执行重命名操作
    for file_path, new_path, file, new_name in rename_operations:
        try:
            os.rename(file_path, new_path)
            print(f"成功移除编号: {file} -> {new_name}")
            processed_count += 1
        except Exception as e:
            print(f"重命名文件时出错: {e}")
    
    # 只有在有处理过的文件时才删除.sorted文件
    if processed_count > 0:
        try:
            os.remove(sorted_file)
            print(f"已删除.sorted文件")
        except Exception as e:
            print(f"删除.sorted文件时出错: {e}")
    
    print("\n处理完成！")
    print(f"共处理: {processed_count} 个文件")

def main(playlist_base_dir):    
    playlists = get_playlists(playlist_base_dir)
    
    # 让用户选择歌单
    selected_playlist = select_playlist(playlists)
    if not selected_playlist:
        return
    
    playlist_dir = os.path.join(playlist_base_dir, selected_playlist)
    playlist_dir_jsonfile = os.path.join(playlist_dir,selected_playlist+".json")
    
    # 选择操作模式
    print("\n请选择操作:")
    print("1. 排序歌曲")
    print("2. 移除编号")
    

    mode = int(input("请输入操作编号: "))
    if mode not in [1, 2]:
        return
    
    if mode == 1:
        # 获取末尾编号
        final_number = get_final_number()
        
        # 读取歌单JSON
        playlist_data = read_playlist_json(playlist_dir_jsonfile)
        if not playlist_data:
            return
        
        tracks = playlist_data.get('tracks', [])
        if not tracks:
            print("歌单中没有歌曲！")
            return
        
        # 重命名音频文件
        rename_audio_files(playlist_dir, tracks, final_number)
    else:
        # 移除编号
        remove_numbers(playlist_dir)

if __name__ == "__main__":
    main()
