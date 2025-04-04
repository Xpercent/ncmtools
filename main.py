#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网易云音乐工具集 - 总控制系统
整合了歌单导出、本地音乐搜索、NCM文件解密等功能

使用方法: python main.py

功能列表:
1. 歌单导出 - 将网易云音乐歌单导出为JSON文件
2. 本地音乐搜索 - 根据歌单在本地查找匹配的音乐文件
3. NCM文件解密 - 将NCM格式文件转换为MP3/FLAC
4. 音乐文件排序 - 对文件夹中的音乐文件进行编号或清除编号
"""

import os
import json
import shutil
from ncm_music_infor_output import extract_playlist_id, get_playlist_info, export_playlist
from find_local_music import load_json_playlist, search_songs_in_local, sanitize_filename
from ncmdump import NeteaseCrypt, process_file, process_directory
from sortlist import sort_music_files, clear_numbers

# 全局配置
CONFIG = {
    "default_music_dir": "F:\\CloudMusic",
    "jsonlist_dir": "jsonlist",
    "playlist_dir": "Myplaylist",
    "dll_path": "./libncmdump.dll"
}


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """打印程序头部"""
    clear_screen()
    print("=" * 60)
    print("                 网易云音乐工具集                  ")
    print("=" * 60)
    print("版本: 1.0.0  作者:Xpercent-YX")
    print("=" * 60)


def print_menu():
    """打印主菜单"""
    print("\n请选择功能:")
    print("  1. 歌单导出 - 将网易云音乐歌单导出为JSON文件")
    print("  2. 本地音乐搜索 - 根据歌单在本地查找匹配的音乐文件")
    print("  3. NCM文件解密 - 将NCM格式文件转换为MP3/FLAC")
    print("  4. 音乐文件排序 - 对文件夹中的音乐文件进行编号或清除编号")
    print("  0. 退出")
    print("=" * 60)


def get_user_choice(max_choice):
    """获取用户选择"""
    while True:
        try:
            choice = int(input("请输入选项编号: "))
            if 0 <= choice <= max_choice:
                return choice
            print(f"无效选项，请输入0-{max_choice}之间的数字")
        except ValueError:
            print("请输入有效的数字")


def wait_for_user():
    """等待用户按键继续"""
    input("\n按回车键返回主菜单...")


def export_playlist_ui():
    """歌单导出功能UI"""
    print("\n== 歌单导出 ==")
    print("此功能允许您将网易云音乐歌单导出为JSON文件")
    
    # 获取歌单ID
    playlist_id_or_url = input("\n请输入歌单ID或链接: ")
    if not playlist_id_or_url.strip():
        print("歌单ID不能为空")
        wait_for_user()
        return
    
    try:
        # 提取歌单ID并获取歌单信息
        playlist_id = extract_playlist_id(playlist_id_or_url)
        playlist_info = get_playlist_info(playlist_id)
        playlist_name = playlist_info['playlist']['name']
        default_filename = sanitize_filename(playlist_name)
        
        # 获取自定义输出文件名
        output_file = input(f"\n请输入输出文件名 (不含扩展名，留空则使用歌单名 '{default_filename}'): ")
        output_file = output_file.strip() or default_filename
        
        # 确保jsonlist文件夹存在
        jsonlist_dir = CONFIG["jsonlist_dir"]
        os.makedirs(jsonlist_dir, exist_ok=True)
        
        # 导出歌单为JSON
        print("\n正在导出歌单...")
        json_file = os.path.join(jsonlist_dir, f"{output_file}.json")
        export_playlist(playlist_info, json_file, True, False, True)
        print(f"已导出JSON格式到: {json_file}")
        print("\n歌单导出成功!")
    except Exception as e:
        print(f"\n导出过程中发生错误: {e}")
        print("\n歌单导出失败")
    
    wait_for_user()


def find_local_music_ui():
    """本地音乐搜索功能UI"""
    print("\n== 本地音乐搜索 ==")
    print("此功能允许您根据导出的歌单文件在本地查找匹配的音乐文件")
    
    try:
        # 查找可用的JSON歌单文件
        jsonlist_dir = CONFIG["jsonlist_dir"]
        json_files = []
        
        if os.path.exists(jsonlist_dir) and os.path.isdir(jsonlist_dir):
            json_files = [f for f in os.listdir(jsonlist_dir) if f.lower().endswith('.json')]
        
        # 用户选择JSON文件
        json_file = ""
        if json_files:
            print("\n可用的歌单文件:")
            for i, file in enumerate(json_files, 1):
                print(f"  {i}. {file}")
            
            choice = input("\n请选择歌单文件编号 (或直接输入文件路径): ")
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(json_files):
                    json_file = os.path.join(jsonlist_dir, json_files[choice_num-1])
                    print(f"已选择: {json_file}")
                else:
                    print(f"无效的编号: {choice}")
                    json_file = input("\n请输入JSON歌单文件路径 (默认: output.json): ")
            except ValueError:
                json_file = choice
        else:
            print(f"\n未在{jsonlist_dir}目录中找到歌单文件")
            json_file = input("\n请输入JSON歌单文件路径 (默认: output.json): ")
        
        # 处理默认值和路径问题
        json_file = json_file.strip() or "output.json"
        
        # 检查文件是否在jsonlist目录中
        if not os.path.isabs(json_file) and not json_file.startswith(jsonlist_dir) and not os.path.exists(json_file):
            possible_path = os.path.join(jsonlist_dir, json_file)
            if os.path.exists(possible_path):
                json_file = possible_path
        
        if not os.path.exists(json_file):
            print(f"错误: 找不到文件 '{json_file}'")
            wait_for_user()
            return
        
        # 获取本地音乐目录
        music_dir = input(f"\n请输入本地音乐目录路径 (默认: {CONFIG['default_music_dir']}): ")
        music_dir = music_dir.strip() or CONFIG['default_music_dir']
        
        if not os.path.exists(music_dir):
            print(f"错误: 目录不存在 '{music_dir}'")
            wait_for_user()
            return
        
        # 是否使用模糊匹配
        fuzzy = input("\n是否使用模糊匹配? (y/n，默认: n): ").lower() == 'y'
        
        # 设置目标目录
        playlist_name = os.path.splitext(os.path.basename(json_file))[0]
        target_dir = os.path.join(CONFIG["playlist_dir"], playlist_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制歌单信息文件到目标目录
        shutil.copy2(json_file, os.path.join(target_dir, 'infor.json'))
        
        # 执行搜索
        print("\n开始搜索本地音乐...")
        playlist_data = load_json_playlist(json_file)
        if not playlist_data:
            print("加载歌单数据失败")
            wait_for_user()
            return
        
        # 搜索匹配的本地音乐
        result = search_songs_in_local(
            playlist_data,
            music_dir,
            recursive=True,
            fuzzy=fuzzy,
            verbose=True,
            copy_to=target_dir,
            no_confirm=False
        )
        
        # 处理NCM文件
        if result and result.get('copied_count', 0) > 0:
            # 检查目标目录中是否有NCM文件
            has_ncm_files = any(file.lower().endswith('.ncm') 
                               for root, _, files in os.walk(target_dir) 
                               for file in files)
            
            if has_ncm_files:
                print(f"\n检测到 {target_dir} 目录中包含NCM加密文件，正在解密")
                decrypt_ncm_files(target_dir, target_dir)
    
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
    
    wait_for_user()


def decrypt_ncm_files(input_dir, output_dir, delete_source=True):
    """解密NCM文件的通用函数"""
    dll_path = CONFIG["dll_path"]
    if not os.path.exists(dll_path):
        print(f"错误: 找不到 '{dll_path}' 文件，无法解密")
        return False
    
    try:
        # 初始化NCM处理器
        ncm_handler = NeteaseCrypt(dll_path)
        if not ncm_handler.is_loaded():
            print("初始化NCM处理器失败，无法解密")
            return False
        
        # 处理目录
        total, success = process_directory(
            ncm_handler, 
            input_dir, 
            output_dir, 
            recursive=True, 
            verbose=True
        )
        
        print(f"\n解密完成: 共处理 {total} 个NCM文件，成功 {success} 个")
        
        # 删除已解密的NCM文件
        if success > 0 and delete_source:
            print("\n正在删除已解密的NCM文件...")
            deleted_count = 0
            
            for root, _, files in os.walk(input_dir):
                for file in files:
                    if file.lower().endswith('.ncm'):
                        try:
                            os.remove(os.path.join(root, file))
                            deleted_count += 1
                        except Exception as e:
                            print(f"删除文件失败: {e}")
            
            print(f"删除完成: 共删除 {deleted_count} 个NCM文件")
        
        return True
    except Exception as e:
        print(f"解密过程中发生错误: {e}")
        return False


def decrypt_ncm_ui():
    """NCM文件解密功能UI"""
    print("\n== NCM文件解密 ==")
    print("此功能允许您将网易云音乐的NCM格式文件转换为MP3/FLAC")
    
    # 检查DLL文件
    dll_path = CONFIG["dll_path"]
    if not os.path.exists(dll_path):
        print(f"错误: 找不到 '{dll_path}' 文件，无法使用解密功能")
        wait_for_user()
        return
    
    # 获取输入路径
    input_path = input("\n请输入NCM文件或目录的路径: ")
    if not input_path.strip():
        print("路径不能为空")
        wait_for_user()
        return
    
    if not os.path.exists(input_path):
        print(f"错误: 路径不存在 '{input_path}'")
        wait_for_user()
        return
    
    # 获取输出目录
    output_dir = input("\n请输入输出目录 (留空则与输入相同): ")
    output_dir = output_dir.strip()
    
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"已创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            wait_for_user()
            return
    
    # 是否删除源文件
    delete_source = input("\n解密后是否删除原NCM文件? (y/n，默认: y): ").lower() != 'n'
    
    try:
        print("\n开始解密...")
        ncm_handler = NeteaseCrypt(dll_path)
        
        if not ncm_handler.is_loaded():
            print("初始化NCM处理器失败，无法解密")
            wait_for_user()
            return
        
        if os.path.isfile(input_path):
            # 处理单个文件
            if input_path.lower().endswith('.ncm'):
                if process_file(ncm_handler, input_path, output_dir, True):
                    print("\n文件解密成功!")
                    
                    # 删除源文件
                    if delete_source:
                        try:
                            os.remove(input_path)
                            print("已删除源NCM文件")
                        except Exception as e:
                            print(f"删除源文件失败: {e}")
                else:
                    print("\n文件解密失败")
            else:
                print(f"错误: 文件不是NCM格式 '{input_path}'")
        else:
            # 处理目录
            total, success = process_directory(
                ncm_handler, 
                input_path, 
                output_dir, 
                recursive=True, 
                verbose=True
            )
            
            print(f"\n解密完成: 共处理 {total} 个NCM文件，成功 {success} 个")
            
            # 删除已解密的NCM文件
            if success > 0 and delete_source:
                print("\n正在删除已解密的NCM文件...")
                deleted_count = 0
                
                for root, _, files in os.walk(input_path):
                    for file in files:
                        if file.lower().endswith('.ncm'):
                            try:
                                os.remove(os.path.join(root, file))
                                deleted_count += 1
                            except Exception as e:
                                print(f"删除文件失败: {e}")
                
                print(f"删除完成: 共删除 {deleted_count} 个NCM文件")
    
    except Exception as e:
        print(f"解密过程中发生错误: {e}")
    
    wait_for_user()


def sort_playlist_ui():
    """音乐文件排序功能UI"""
    print("\n== 音乐文件排序 ==")
    print("此功能允许您对音乐文件进行编号排序或清除编号")
    
    # 获取歌单目录
    playlist_dir = CONFIG["playlist_dir"]
    if os.path.exists(playlist_dir) and os.path.isdir(playlist_dir):
        playlists = [d for d in os.listdir(playlist_dir) if os.path.isdir(os.path.join(playlist_dir, d))]
    else:
        playlists = []
    
    # 选择歌单
    target_dir = ""
    if playlists:
        print("\n可用的歌单目录:")
        for i, pl in enumerate(playlists, 1):
            print(f"  {i}. {pl}")
        
        choice = input("\n请选择歌单目录编号 (或直接输入目录路径): ")
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(playlists):
                target_dir = os.path.join(playlist_dir, playlists[choice_num-1])
                print(f"已选择: {target_dir}")
            else:
                print(f"无效的编号: {choice}")
                target_dir = input("\n请输入歌单目录路径: ")
        except ValueError:
            target_dir = choice
    else:
        print(f"\n未在 {playlist_dir} 目录中找到歌单目录")
        target_dir = input("\n请输入歌单目录路径: ")
    
    # 检查目录是否存在
    if not target_dir.strip() or not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        print(f"错误: 无效的目录 '{target_dir}'")
        wait_for_user()
        return
    
    # 操作类型
    print("\n请选择操作:")
    print("  1. 对文件进行编号")
    print("  2. 清除文件编号")
    
    op_choice = get_user_choice(2)
    
    try:
        if op_choice == 1:
            # 获取最大编号
            last_num = input("\n请输入末尾编号 (即最后一首歌的编号，默认: 100): ")
            try:
                last_num = int(last_num) if last_num.strip() else 100
                if last_num <= 0:
                    raise ValueError("编号必须大于0")
            except ValueError:
                print("无效的编号，使用默认值100")
                last_num = 100
            
            # 执行排序
            print(f"\n正在对 '{target_dir}' 中的音乐文件进行编号...")
            if sort_music_files(target_dir, last_num):
                print("\n排序完成!")
            else:
                print("\n排序失败或没有可排序的文件")
        else:
            # 执行清除编号
            print(f"\n正在清除 '{target_dir}' 中的文件编号...")
            if clear_numbers(target_dir):
                print("\n清除编号完成!")
            else:
                print("\n清除编号失败或没有已排序的文件")
    
    except Exception as e:
        print(f"排序过程中发生错误: {e}")
    
    wait_for_user()


def load_config():
    """加载配置文件"""
    try:
        config_file = 'config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                CONFIG.update(user_config)
    except Exception as e:
        print(f"加载配置文件失败: {e}")


def main():
    """主函数"""
    load_config()
    
    while True:
        print_header()
        print_menu()
        choice = get_user_choice(4)
        
        if choice == 0:
            print("\n感谢使用网易云音乐工具集，再见!")
            break
        elif choice == 1:
            export_playlist_ui()
        elif choice == 2:
            find_local_music_ui()
        elif choice == 3:
            decrypt_ncm_ui()
        elif choice == 4:
            sort_playlist_ui()


if __name__ == "__main__":
    main()