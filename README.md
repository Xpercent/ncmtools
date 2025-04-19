# 网易云音乐工具集

一个功能强大的Python工具集，用于下载、管理和整理网易云音乐歌单。
由pyncm提供api支持，在此特别鸣谢pyncm

## 功能概述

1. **歌单下载** - 下载网易云音乐歌单
2. **歌单导出** - 将网易云音乐歌单导出为JSON文件
3. **音乐文件排序** - 对文件夹中的音乐文件进行编号或清除编号
4. **默认参数设置** - 设置默认参数包括cookie等

## 文件结构

```
.
├── main.py                # 主程序入口
├── config.json            # 配置文件
├── globle_func.py         # 全局功能函数
├── search_playlist.py     # 歌单搜索与导出功能
└── sort_playlist.py       # 音乐文件排序功能
```

## 详细功能说明
```
### 1. 主程序 (main.py)

- 提供用户友好的命令行界面
- 集成所有功能模块
- 管理配置设置
- 功能菜单：
  - 歌单下载
  - 歌单导出
  - 音乐文件排序
  - 默认参数设置

### 2. 全局功能 (globle_func.py)

- `sanitize_filename()`: 清理文件名，替换Windows系统不允许的字符
- `save_json()`/`load_json()`: JSON文件读写功能
- `normalize_playlist()`: 规范化歌单ID或URL格式

### 3. 歌单搜索与导出 (search_playlist.py)

- 获取歌单完整信息
- 批量获取歌曲详情
- 将歌单信息导出为JSON文件
- 支持歌单ID或URL输入

### 4. 音乐文件排序 (sort_playlist.py)

- 为音乐文件添加序号前缀
- 移除已有的序号前缀
- 支持多种音频格式(.mp3, .flac, .wav, .ogg)
- 自动处理对应的歌词文件(.lrc)
- 使用模糊匹配算法关联歌单与本地文件
- 记录排序状态(.sorted文件)
```

## 配置说明

默认配置文件`config.json`包含以下设置：
PS: 由于某些原因导致cookie必须为正确cookie，否则在下载歌单时会报错，因此请填入正确的cookie或清空cookie
```json
{
    "pyncm_command": "--quality exhigh --lyric-no \"tlyric romalrc yrc\" --no-overwrite",
    "playlist_dir": "Myplaylist",
    "cookie": "网易云音乐MUSIC_U Cookie"
}
```

## 使用说明

1. 安装依赖：
   ```bash
   pip install pyncm
   ```

2. 运行程序：
   ```bash
   python main.py
   ```

3. 按照菜单提示选择功能

4. 首次使用建议：
   - 在"默认参数设置"中配置你的网易云音乐Cookie
   - 设置你喜欢的下载参数和保存目录

## 注意事项

1. 使用下载功能需要有效的网易云音乐Cookie(MUSIC_U)
2. 高音质下载可能需要VIP权限
3. VIP歌曲只有设置Cookie才可以下载完整，否则只能下前30秒
4. 文件排序功能依赖于歌单导出的JSON文件
5. 程序会自动创建歌单保存目录

## 作者信息

- 版本: 2.0.0
- 作者: Xpercent-YX

## 声明
本工具仅用于个人学习和研究，请勿用于任何商业用途。使用本工具处理音乐文件时，请遵守相关法律法规，尊重音乐版权。
