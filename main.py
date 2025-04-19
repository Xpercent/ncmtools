#!/usr/bin/env python
# -*- coding: utf-8 -*-
from search_playlist import main as search_main
from sort_playlist import main as sort_main
from globle_func import sanitize_filename,load_json,save_json,normalize_playlist
import os,sys,shlex
from subprocess import run
from pyncm.apis import playlist
default_config = {
    "pyncm_command": '--quality exhigh --lyric-no "tlyric romalrc yrc" --no-overwrite',
    "playlist_dir": "Myplaylist",
    "cookie": ""
}
CONFIG = default_config.copy()

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')
def print_header():
    """打印程序头部"""
    clear_screen()
    print("=" * 60)
    print("                 网易云音乐工具集                  ")
    print("=" * 60)
    print("版本: 2.0.0  作者:Xpercent-YX")
    print("=" * 60)
def print_menu():
    """打印主菜单"""
    print("\n请选择功能:")
    print("  1. 歌单下载 - 下载网易云音乐歌单")
    print("  2. 歌单导出 - 将网易云音乐歌单导出为JSON文件")
    print("  3. 音乐文件排序 - 对文件夹中的音乐文件进行编号或清除编号")
    print("  4. 默认参数设置 - 设置默认参数包括cookie等")
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

def get_resource_path(relative_path):
    """ 获取打包后的资源路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_resource_path(relative_path):
    """ 获取打包后的资源路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def pyncm_cli_ui():
    while True:
            input1 = input("请输入歌单ID或歌单链接: ").strip()
            if not input1:
                print("输入不能为空，请重新输入")
                continue
            playlistid = normalize_playlist(input1,"id")
            playlisturl = normalize_playlist(input1,"url")

            result = playlist.GetPlaylistInfo(playlistid)
            safe_name = f"{CONFIG['playlist_dir']}/{sanitize_filename(result['playlist']['name'])}"

            input2 = input(f'请输入pyncm命令行参数(默认{CONFIG["pyncm_command"]} --output "{safe_name}"): ').strip()
            if not input2:
                input2 = f'{CONFIG["pyncm_command"]} --output "{safe_name}"'
            break
    command_string = f'{playlisturl} {input2}'
    # original_argv = sys.argv.copy()
    # try:
    #     # 将命令字符串分割为参数列表
    #     args = shlex.split(command_string)
    #     # 设置新的参数列表 (保留脚本名称)
    #     sys.argv = [original_argv[0]] + args
    #     # 调用cli模块的main函数
    #     pyncmcli_main()
    # finally:
    #     # 恢复原始参数
    #     sys.argv = original_argv
    exe_path = get_resource_path("pyncm.exe")

    cmd = [exe_path]#sys.executable,
    cmd.extend(shlex.split(command_string))
    if CONFIG["cookie"]:
        cmd.extend(["--cookie", CONFIG["cookie"]])
    try:
        run(cmd, check=True)
    finally:
        search_main(playlistid, CONFIG['playlist_dir'])
        wait_for_user()

def search_playlist_ui():
    while True:
            input1 = input("请输入歌单ID或歌单链接: ").strip()
            if not input1:
                print("输入不能为空，请重新输入")
                continue
            break
    result = search_main(input1, CONFIG["playlist_dir"])
    wait_for_user()

def sort_playlist_ui():
    result = sort_main(CONFIG["playlist_dir"])
    wait_for_user()
    
def default_set_ui():
    """默认参数设置界面"""
    while True:
        print("\n当前默认参数设置:")
        print(f"  1. pyncm下载参数: {CONFIG['pyncm_command']}")
        print(f"  2. 歌单保存目录: {CONFIG['playlist_dir']}")
        print(f"  3. Cookie设置: {CONFIG['cookie'][:20] + '...' if CONFIG['cookie'] else '未设置'}")
        print("  4. 重置设置")
        print("  5. 保存并返回")
        print("  0. 不保存返回")
        choice = get_user_choice(5)
        if choice == 0:
            return
        elif choice == 1:
            print(pyncm_help)
            new_value = input(f"请输入新的pyncm下载参数(当前: {CONFIG['pyncm_command']}): ").strip()
            if new_value:
                CONFIG['pyncm_command'] = new_value
                print("pyncm下载参数已更新")
        elif choice == 2:
            new_value = input(f"请输入新的歌单保存目录(当前: {CONFIG['playlist_dir']}): ").strip()
            if new_value:
                CONFIG['playlist_dir'] = new_value
                print("歌单保存目录已更新")
        elif choice == 3:
            new_value = input("请输入网易云音乐Cookie(留空则清除): ").strip()
            CONFIG['cookie'] = new_value if new_value else None
            print("Cookie设置已更新")
        elif choice == 4:
            CONFIG.update(default_config)
            save_json("config.json", default_config)
            print("配置已重置")
            break
        elif choice == 5:
            save_json("config.json", CONFIG)
            print("配置已保存")
            break
    
    wait_for_user()

def main():
    data = load_json("config.json")
    if data:
        CONFIG.update(data)
    while True:
        print_header()
        print_menu()

        

        choice = get_user_choice(4)  # 有4个功能选项
        if choice == 0:
            print("\n感谢使用网易云音乐工具集，再见！")
            break
        elif choice == 1:
            pyncm_cli_ui()
        elif choice == 2:
            search_playlist_ui()
        elif choice == 3:
            sort_playlist_ui()       
        elif choice == 4:
            default_set_ui()

pyncm_help = """usage: pyncm_cli.py [-h] [--max-workers 最多同时下载任务数] [--output-name 保存文件名模板] [-o 输出] [--quality 音质] [-dl] [--no-overwrite] [--lyric-no 跳过歌词] [--phone 手机] [--cookie Cookie MUSIC_U]
                    [--pwd 密码] [--save [保存到]] [--load [保存的登陆信息文件]] [--http] [--deviceId 设备ID] [--log-level LOG_LEVEL] [-n 下载总量] [--sort-by 歌曲排序] [--reverse-sort] [--user-bookmarks]
                    [--save-m3u 保存M3U播放列表文件名]
                    [链接 ...]

PyNCM 网易云音乐下载工具 1.7.1

positional arguments:
  链接                    网易云音乐分享链接

options:
  -h, --help            show this help message and exit

下载:
  --max-workers 最多同时下载任务数, -m 最多同时下载任务数
  --output-name 保存文件名模板, --template 保存文件名模板, -t 保存文件名模板
                        保存文件名模板
                            参数：    
                                id     - 网易云音乐资源 ID
                                year   - 出版年份
                                no     - 专辑中编号
                                album  - 专辑标题
                                track  - 单曲标题        
                                title  - 完整标题
                                artists- 艺术家名
                            例：
                                {track} - {artists} 等效于 {title}
  -o 输出, --output 输出    输出文件夹
                            注：该参数也可使用模板，格式同 保存文件名模板
  --quality 音质          音频音质（高音质需要 CVIP）
                            参数：
                                hires  - Hi-Res
                                lossless- "无损"
                                exhigh  - 较高
                                standard- 标准
  -dl, --use-download-api
                        调用下载API，而非播放API进行下载。如此可能允许更高高音质音频的下载。
                        【注意】此API有额度限制，参考 https://music.163.com/member/downinfo
  --no-overwrite        不重复下载已经存在的音频文件

歌词:
  --lyric-no 跳过歌词       跳过某些歌词类型的下载
                            参数：
                                lrc    - 源语言歌词  (合并到 .lrc)
                                tlyric - 翻译后歌词  (合并到 .lrc)
                                romalrc- 罗马音歌词  (合并到 .lrc)
                                yrc    - 逐词滚动歌词 (保存到 .ass)
                                none   - 下载所有歌词
                            例：
                                --lyric-no "tlyric romalrc yrc" 将只下载源语言歌词
                                --lyric-no none 将下载所有歌词
                            注：
                                默认不下载 *逐词滚动歌词*


登陆:
  --phone 手机            网易账户手机号
  --cookie Cookie (MUSIC_U)
                        网易云音乐 MUSIC_U Cookie (形如 '00B2471D143...')
  --pwd 密码, --password 密码
                        网易账户密码
  --save [保存到]          写本次登录信息于文件
  --load [保存的登陆信息文件]    从文件读取登录信息供本次登陆使用
  --http                优先使用 HTTP，不保证不被升级
  --deviceId 设备ID       指定设备 ID；匿名登陆时，设备 ID 既指定对应账户
                        【注意】默认 ID 与当前设备无关，乃从内嵌 256 可用 ID 中随机选取；指定自定义 ID 不一定能登录，相关性暂时未知
  --log-level LOG_LEVEL
                        日志等级

限量及过滤（注：只适用于*每单个*链接 / ID）:
  -n 下载总量, --count 下载总量
                        限制下载歌曲总量，n=0即不限制（注：过大值可能导致限流）
  --sort-by 歌曲排序        【限制总量时】歌曲排序方式 (default: 默认排序 hot: 热度高（相对于其所在专辑）在前 time: 发行时间新在前)
  --reverse-sort        【限制总量时】倒序排序歌曲
  --user-bookmarks      【下载用户歌单时】在下载用户创建的歌单的同时，也下载其收藏的歌单

工具:
  --save-m3u 保存M3U播放列表文件名
                        将本次下载的歌曲文件名依一定顺序保存在M3U文件中；写入的文件目录相对于该M3U文件
                                文件编码为 UTF-8
                                顺序为：链接先后优先——每个链接的所有歌曲依照歌曲排序设定 （--sort-by）排序"""

if __name__ == "__main__":
    main()

