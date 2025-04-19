import json
def sanitize_filename(filename):
    """
    清理文件名，替换Windows系统不允许的字符
    替换规则：
    / -> ／ (全角斜杠)
    \ -> ＼ (全角反斜杠)
    : -> ： (全角冒号)
    * -> ＊ (全角星号)
    ? -> ？ (全角问号)
    " -> ＂ (全角引号)
    < -> ＜ (全角小于号)
    > -> ＞ (全角大于号)
    | -> ｜ (全角竖线)
    """
    # 定义替换字典
    replacements = {
        '/': '／',
        '\\': '＼',
        ':': '：',
        '*': '＊',
        '?': '？',
        '"': '＂',
        '<': '＜',
        '>': '＞',
        '|': '｜'
    }
    # 替换非法字符
    for char, replacement in replacements.items():
        filename = filename.replace(char, replacement)
    return filename

def save_json(output_file, data):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False
    
def load_json(inputfile):
    try:
        with open(inputfile, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"加载文件失败: {e}")
        return False
    return data
import re

def normalize_playlist(input_str: str, output_format: str = 'id') -> str:
    """
    参数:
        input_str: 输入字符串（可以是ID或URL）
        output_format: 输出格式，'id' 或 'url'，默认为 'id'
    示例:
        >>> normalize_playlist("13577478110")
        "13577478110"
        >>> normalize_playlist("https://music.163.com/playlist?id=13577478110", 'url')
        "https://music.163.com/playlist?id=13577478110"
    """
    # 定义正则模式，匹配URL中的播放列表ID
    URL_PATTERN = r'(?:playlist[?/]id=|playlist/)(\d+)'
    
    # 提取playlist_id
    if input_str.isdigit():
        playlist_id = input_str
    else:
        match = re.search(URL_PATTERN, input_str)
        if not match:
            raise ValueError(f"无法从输入 '{input_str}' 中提取播放列表ID")
        playlist_id = match.group(1)
    
    # 根据要求返回对应格式
    if output_format == 'id':
        return playlist_id
    if output_format == 'url':
        return f"https://music.163.com/playlist?id={playlist_id}"
    
    raise ValueError(f"无效的输出格式 '{output_format}'，必须是 'id' 或 'url'")