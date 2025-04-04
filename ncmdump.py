#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NCM音乐文件解密工具
将网易云音乐的NCM加密文件转换为正常的音频文件(MP3/FLAC)

此模块提供了用于解密NCM文件的类和函数，可被其他程序导入使用
"""

import os
import ctypes
from ctypes import c_char_p, c_int, c_void_p


def parse_args():
    """解析命令行参数"""
    import argparse
    parser = argparse.ArgumentParser(description="NCM音乐文件解密工具")
    parser.add_argument("input_path", help="NCM文件或包含NCM文件的目录路径")
    parser.add_argument("-o", "--output", default="", help="输出目录路径，默认与输入文件相同的目录")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录中的文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("-d", "--delete", action="store_true", help="转换成功后删除原NCM文件")
    parser.add_argument("--dll-path", default="libncmdump.dll", help="libncmdump.dll的路径")
    return parser.parse_args()


class NeteaseCrypt:
    """网易云音乐NCM文件解密类，封装了DLL库的调用"""
    
    def __init__(self, dll_path="libncmdump.dll"):
        """初始化DLL库"""
        self.dll_path = dll_path
        try:
            # 加载DLL库
            self.lib = ctypes.CDLL(dll_path)
            
            # 定义DLL中的函数
            self.lib.CreateNeteaseCrypt.argtypes = [c_char_p]
            self.lib.CreateNeteaseCrypt.restype = c_void_p
            
            self.lib.Dump.argtypes = [c_void_p, c_char_p]
            self.lib.Dump.restype = c_int
            
            self.lib.FixMetadata.argtypes = [c_void_p]
            self.lib.FixMetadata.restype = None
            
            self.lib.DestroyNeteaseCrypt.argtypes = [c_void_p]
            self.lib.DestroyNeteaseCrypt.restype = None
            
            print("成功加载DLL库")
        except Exception as e:
            print(f"加载DLL库失败: {e}")
            self.lib = None
    
    def is_loaded(self):
        """检查DLL是否加载成功"""
        return self.lib is not None
    
    def decrypt_file(self, input_file, output_dir="", delete_source=False):
        """解密单个NCM文件"""
        if not self.is_loaded():
            print("DLL库未加载，无法处理文件")
            return False
        
        try:
            # 将文件路径转换为字节字符串
            input_file_bytes = input_file.encode('utf-8')
            output_dir_bytes = output_dir.encode('utf-8') if output_dir else b""
            
            # 创建NeteaseCrypt实例并执行解密
            ncm_instance = self.lib.CreateNeteaseCrypt(input_file_bytes)
            if not ncm_instance:
                print(f"创建NeteaseCrypt实例失败: {input_file}")
                return False
            
            # 执行解密操作
            result = self.lib.Dump(ncm_instance, output_dir_bytes)
            
            # 修复元数据
            self.lib.FixMetadata(ncm_instance)
            
            # 销毁NeteaseCrypt实例
            self.lib.DestroyNeteaseCrypt(ncm_instance)
            
            # 检查结果并处理源文件
            success = (result == 0)
            if success and delete_source:
                try:
                    os.remove(input_file)
                except Exception as e:
                    print(f"删除源文件失败: {e}")
            
            return success
        except Exception as e:
            print(f"处理文件失败: {e}")
            return False


def process_file(ncm_handler, input_file, output_dir="", verbose=False):
    """处理单个NCM文件"""
    if verbose:
        print(f"正在处理文件: {input_file}")
    
    result = ncm_handler.decrypt_file(input_file, output_dir)
    
    if verbose:
        print(f"处理{'成功' if result else '失败'}: {input_file}")
    
    return result


def process_directory(ncm_handler, input_dir, output_dir="", recursive=False, verbose=False):
    """处理目录中的所有NCM文件"""
    processed_count = 0
    success_count = 0
    
    if verbose:
        print(f"扫描目录: {input_dir}")
    
    if recursive:
        # 递归处理所有子目录
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.ncm'):
                    processed_count += 1
                    
                    # 创建对应的输出目录
                    curr_output_dir = root
                    if output_dir:
                        rel_path = os.path.relpath(root, input_dir)
                        curr_output_dir = os.path.join(output_dir, rel_path)
                        os.makedirs(curr_output_dir, exist_ok=True)
                    
                    # 处理文件
                    if process_file(ncm_handler, os.path.join(root, file), curr_output_dir, verbose):
                        success_count += 1
    else:
        # 只处理当前目录
        for file in os.listdir(input_dir):
            if file.lower().endswith('.ncm'):
                processed_count += 1
                file_path = os.path.join(input_dir, file)
                target_dir = output_dir or input_dir
                if process_file(ncm_handler, file_path, target_dir, verbose):
                    success_count += 1
    
    return processed_count, success_count
