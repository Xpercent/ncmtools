#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网易云音乐歌单导出工具
将网易云音乐歌单中的所有歌曲名导出到json文件

此模块提供了用于导出网易云音乐歌单的功能函数，可以被其他程序导入使用
"""

import re
import json
from pyncm import apis
from pyncm.apis.login import LoginViaAnonymousAccount


def parse_args():
    """解析命令行参数"""
    import argparse
    parser = argparse.ArgumentParser(description="网易云音乐歌单导出工具")
    parser.add_argument("playlist_url", help="网易云音乐歌单链接或ID")
    parser.add_argument("-o", "--output", default="output.json", help="输出文件名")
    parser.add_argument("--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--only-names", action="store_true", help="只导出歌曲名称")
    return parser.parse_args()


def extract_playlist_id(playlist_url):
    """从歌单链接中提取ID"""
    if playlist_url.isdigit():
        return playlist_url
    
    if "163cn.tv" in playlist_url:
        raise ValueError("暂不支持短链接，请使用完整链接或直接输入歌单ID")
    
    # 常规链接格式，例如: https://music.163.com/#/playlist?id=123456789
    match = re.search(r'id=(\d+)', playlist_url)
    if match:
        return match.group(1)
    
    # 分享链接，例如: https://music.163.com/playlist/123456789/123456789
    match = re.search(r'playlist/(\d+)', playlist_url)
    if match:
        return match.group(1)
    
    raise ValueError("无法识别的歌单链接格式，请直接输入歌单ID")


def get_playlist_info(playlist_id):
    """获取歌单信息"""
    try:
        # 登录匿名账号，以获取API访问权限
        LoginViaAnonymousAccount()
        
        # 获取歌单详情
        playlist_info = apis.playlist.GetPlaylistInfo(playlist_id)
        
        # 检查歌单是否存在
        if playlist_info.get('code') != 200:
            error_msg = playlist_info.get('message', '未知错误')
            raise Exception(f"获取歌单失败: {error_msg}")
        
        return playlist_info
    except Exception as e:
        raise Exception(f"获取歌单信息时发生错误: {e}")


def export_playlist(playlist_info, output_file, verbose=False, only_names=False, json_format=True):
    """将歌单信息导出到文件"""
    try:
        # 获取歌单信息
        playlist = playlist_info['playlist']
        playlist_name = playlist['name']
        creator = playlist['creator']['nickname']
        track_count = playlist['trackCount']
        tracks = playlist['tracks']
        
        if verbose:
            print(f"歌单名称: {playlist_name}")
            print(f"创建者: {creator}")
            print(f"歌曲数量: {track_count}")
        
        # 准备JSON数据
        result = {
            "playlist_name": playlist_name,
            "creator": creator,
            "track_count": track_count,
            "tracks": []
        }
        
        for track in tracks:
            track_name = track['name']
            artists = [artist['name'] for artist in track['ar']]
            
            # 创建歌曲信息字典
            track_info = {
                "name": track_name,
                "artists": artists,
                "artist_str": ', '.join(artists)
            }
            
            # 添加额外信息
            if not only_names:
                track_info["album"] = track['al']['name']
                track_info["id"] = track['id']
            
            result["tracks"].append(track_info)
            
            if verbose:
                print(f"导出 {len(result['tracks'])}/{track_count}: {track_name}")
        
        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        if verbose:
            print(f"\n歌单导出完成，已保存到 {output_file}")
        else:
            print(f"成功导出歌单 '{playlist_name}' 中的 {track_count} 首歌曲到 {output_file}")
            
        return True
    except Exception as e:
        print(f"导出歌单时发生错误: {e}")
        return False


def export_playlist_to_json(playlist_id_or_url, output_file="output.json", verbose=False, only_names=False):
    """快速将歌单导出为JSON文件"""
    try:
        playlist_id = extract_playlist_id(playlist_id_or_url)
        playlist_info = get_playlist_info(playlist_id)
        return export_playlist(playlist_info, output_file, verbose, only_names, True)
    except Exception as e:
        print(f"导出歌单到JSON时发生错误: {e}")
        return False