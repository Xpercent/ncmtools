#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyncm import apis
import os
from globle_func import sanitize_filename,save_json,normalize_playlist

def get_playlist_info(playlist_id):
    """获取歌单信息（完整版）"""
    try:
        # 获取歌单基本信息
        result = apis.playlist.GetPlaylistInfo(playlist_id)
        playlist_data = result['playlist']
        
        # 提取所有歌曲ID
        track_ids = [track['id'] for track in playlist_data['trackIds']]
        all_tracks = []
        
        # 分批获取歌曲详情
        batch_size = 1000
        for i in range(0, len(track_ids), batch_size):
            batch_ids = track_ids[i:i+batch_size]
            songs_detail = apis.track.GetTrackDetail(batch_ids)
            if songs_detail.get('code') == 200:
                all_tracks.extend(songs_detail['songs'])
        
        # 提取所需信息
        extracted_data = {
            "id": playlist_data['id'],
            "playlist_name": playlist_data['name'],
            "creator": playlist_data['creator']['nickname'],
            "track_count": len(track_ids),
            "tracks": []
        }
        
        # 处理歌曲信息
        for track in all_tracks:
            # 提取艺术家列表
            artists = []
            artist_str = ""
            if 'ar' in track:
                artists = [artist['name'] for artist in track['ar']]
                artist_str = ",".join(artists)
            
            track_info = {
                #"name": track['name'],
                #"artists": artists,
                #"artist_str": artist_str,
                "full_title": sanitize_filename(f"{track['name']} - {artist_str}"),
                #"id": track['id']
            }
            extracted_data['tracks'].append(track_info)
            
        return extracted_data
    except Exception as e:
        print(f"获取歌单信息失败: {e}")
        return None

def main(playlist_id=None, playlist_dir="Myplaylist"):
    # 获取歌单ID
    if playlist_id is None:
        playlist_id = input("请输入网易云音乐歌单ID或歌单链接: ")
        if not playlist_id:
            print("未提供歌单ID")
            return False
            
    try:
        playlist_id =normalize_playlist(playlist_id,"id")
    except ValueError as e:
        print(f"错误: {e}")
        return False
    
    # 获取歌单信息
    playlist_data = get_playlist_info(playlist_id)
    if not playlist_data:
        print("获取歌单信息失败")
        return False
    
    # 创建保存目录
    safe_name = sanitize_filename(playlist_data['playlist_name'])
    save_dir = f"{playlist_dir}/{safe_name}"
    os.makedirs(save_dir, exist_ok=True)

    output_file = f"{save_dir}/{safe_name}.json"
    
    # 保存到文件
    save_result = save_json(output_file, playlist_data)
    if not save_result:
        print("保存文件失败")
        return False
    
    # 打印简要信息
    print(f"歌单: {playlist_data['playlist_name']}")
    print(f"创建者: {playlist_data['creator']}")
    print(f"歌曲数量: {playlist_data['track_count']}")
    print(f"已成功保存到: {output_file}")

    return True

if __name__ == "__main__":
    main()