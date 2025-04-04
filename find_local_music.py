#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地音乐搜索工具
根据网易云音乐歌单JSON文件，在本地音乐目录中搜索匹配的歌曲文件，并将匹配到的文件复制到指定目录
"""

import os
import json
import re
import shutil


def parse_args():
    """解析命令行参数"""
    import argparse
    parser = argparse.ArgumentParser(description="本地音乐搜索工具")
    parser.add_argument("json_file", help="网易云音乐歌单JSON文件路径")
    parser.add_argument("-d", "--directory", default="F:\\CloudMusic", help="本地音乐目录路径")
    parser.add_argument("--no-recursive", action="store_true", help="不递归搜索子目录")
    parser.add_argument("--fuzzy", action="store_true", help="使用模糊匹配")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--copy-to", help="将找到的音乐文件复制到指定目录")
    parser.add_argument("--no-confirm", action="store_true", help="复制文件时不要求确认")
    return parser.parse_args()


def load_json_playlist(json_file):
    """加载JSON格式的歌单文件"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            playlist_data = json.load(f)
        
        if "tracks" not in playlist_data:
            print(f"错误: JSON文件 '{json_file}' 不包含 'tracks' 字段")
            return None
        
        return playlist_data
    except Exception as e:
        print(f"读取JSON文件时发生错误: {e}")
        return None


def normalize_string(s):
    """标准化字符串，移除特殊字符，转为小写"""
    return re.sub(r'[^\w\s]', '', s).lower().strip()


def sanitize_filename(filename):
    """清理文件名，移除不允许的字符"""
    return re.sub(r'[\\/:*?"<>|]', '_', filename)


def find_local_files(directory, recursive=True, extensions=None):
    """查找指定目录下的所有音乐文件"""
    if extensions is None:
        extensions = ['.mp3', '.flac', '.wav', '.ncm']
    
    music_files = []
    extensions = [ext.lower() for ext in extensions]
    
    try:
        if recursive:
            for root, _, files in os.walk(directory):
                music_files.extend(os.path.join(root, file) for file in files 
                                 if os.path.splitext(file)[1].lower() in extensions)
        else:
            music_files = [os.path.join(directory, file) for file in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, file)) 
                         and os.path.splitext(file)[1].lower() in extensions]
    except Exception as e:
        print(f"搜索目录时发生错误: {e}")
    
    return music_files


def match_song(song, local_files, fuzzy=False):
    """查找与歌曲匹配的本地文件"""
    song_name = song.get('name', '')
    artists = song.get('artists', [])
    artist_str = song.get('artist_str', '')
    matches = []
    
    for file_path in local_files:
        file_name = os.path.basename(file_path)
        
        if not fuzzy:
            if song_name in file_name and (any(artist in file_name for artist in artists) or artist_str in file_name):
                matches.append(file_path)
        else:
            file_name_norm = normalize_string(file_name)
            song_name_norm = normalize_string(song_name)
            
            if song_name_norm in file_name_norm and any(normalize_string(artist) in file_name_norm for artist in artists):
                matches.append(file_path)
    
    return matches


def copy_file_to_playlist(source_file, target_dir, index=None, song_name=None, artist=None, verbose=False):
    """复制文件到目标目录"""
    os.makedirs(target_dir, exist_ok=True)
    source_filename = os.path.basename(source_file)
    target_path = os.path.join(target_dir, source_filename)
    
    # 检查目标文件是否已存在
    if os.path.exists(target_path):
        if verbose:
            print(f"文件已存在: {target_path}")
        return False
    
    # 检查是否为NCM文件，以及目标目录中是否已有对应的解码文件
    if source_file.lower().endswith('.ncm') and song_name:
        file_base_name = os.path.splitext(source_filename)[0]
        
        # 检查是否已存在同名的mp3或flac文件
        for ext in ['.mp3', '.flac']:
            if os.path.exists(os.path.join(target_dir, f"{file_base_name}{ext}")):
                if verbose:
                    print(f"跳过NCM文件，因为已存在解码后的文件")
                return False
        
        # 基于歌曲名和艺术家搜索可能已存在的解码文件
        if song_name and artist:
            for filename in os.listdir(target_dir):
                if (os.path.isfile(os.path.join(target_dir, filename)) and 
                    filename.lower().endswith(('.mp3', '.flac')) and
                    song_name in filename and artist in filename):
                    if verbose:
                        print(f"跳过NCM文件，因为找到可能匹配的解码文件")
                    return False
    
    try:
        shutil.copy2(source_file, target_path)
        if verbose:
            print(f"复制文件成功: {source_file} -> {target_path}")
        return True
    except Exception as e:
        print(f"复制文件失败 {source_file}: {e}")
        return False


def search_songs_in_local(playlist_data, local_directory, recursive=True, fuzzy=False, verbose=False, 
                          copy_to=None, rename=False, no_confirm=False):
    """在本地目录中搜索歌单中的歌曲"""
    if verbose:
        print(f"搜索目录: {local_directory}，递归搜索: {'是' if recursive else '否'}")
        print("正在扫描本地音乐文件...")
    
    local_files = find_local_files(local_directory, recursive)
    
    tracks = playlist_data.get('tracks', [])
    playlist_name = playlist_data.get('playlist_name', '未命名歌单')
    
    if verbose:
        print(f"找到 {len(local_files)} 个本地音乐文件")
        print(f"歌单名称: {playlist_name}，歌曲数量: {len(tracks)}")
    
    # 匹配结果统计
    found_count = 0
    not_found = []
    copy_success_count = 0
    found_songs = []
    
    print(f"\n{'=' * 60}")
    print(f"歌单 '{playlist_name}' 在本地的匹配结果:")
    print(f"{'=' * 60}\n")
    
    # 遍历歌单中的每首歌曲
    for index, song in enumerate(tracks, 1):
        song_name = song.get('name', '未知歌曲')
        artist_str = song.get('artist_str', '未知艺术家')
        
        matches = match_song(song, local_files, fuzzy)
        
        if matches:
            found_count += 1
            found_songs.append({
                'index': index,
                'song_name': song_name,
                'artist': artist_str,
                'file_path': matches[0]  # 如果有多个匹配，只使用第一个
            })
            print(f"{index}. 【已找到】 {song_name} - {artist_str}")
            for match in matches:
                print(f"   - {match}")
        else:
            not_found.append((song_name, artist_str))
            print(f"{index}. 【未找到】 {song_name} - {artist_str}")
    
    # 打印统计信息
    print(f"\n{'=' * 60}")
    print(f"匹配完成: 共 {len(tracks)} 首歌曲，找到 {found_count} 首，未找到 {len(not_found)} 首")
    print(f"匹配率: {found_count / len(tracks) * 100:.1f}%")
    
    if verbose and not_found:
        print("\n未找到的歌曲:")
        for i, (name, artist) in enumerate(not_found, 1):
            print(f"{i}. {name} - {artist}")
    
    # 如果需要复制找到的歌曲
    if found_songs:
        target_dir = copy_to if copy_to else playlist_name
        
        if not no_confirm:
            confirmation = input(f"\n是否将 {found_count} 首找到的歌曲复制到 '{target_dir}'？(y/n 默认:y): ")
            if confirmation.strip() and confirmation.lower() != 'y':
                print("已取消复制操作")
                return
        
        os.makedirs(target_dir, exist_ok=True)
        
        print(f"\n开始复制歌曲到 '{target_dir}'...")
        for song in found_songs:
            if copy_file_to_playlist(
                song['file_path'], 
                target_dir, 
                song['index'], 
                song['song_name'], 
                song['artist'], 
                verbose
            ):
                copy_success_count += 1
        
        print(f"复制完成: 共复制 {copy_success_count} 首歌曲到 '{target_dir}'")
    
    # 返回匹配结果
    return {
        'found_count': found_count,
        'found_songs': found_songs,
        'not_found': not_found,
        'copied_count': copy_success_count
    }