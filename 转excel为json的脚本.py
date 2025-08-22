#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel转JSON脚本
支持将包含"单字拼音"、"汉字"、"词"、"词拼音"四列的xlsx文件转换为JSON格式
"""

import pandas as pd
import json
import os
import sys
from typing import List, Dict, Any

def excel_to_json(excel_file_path: str, output_file_path: str = None) -> List[Dict[str, Any]]:
    """
    将Excel文件转换为JSON格式
    
    Args:
        excel_file_path: Excel文件路径
        output_file_path: 输出JSON文件路径（可选）
    
    Returns:
        转换后的数据列表
    """
    try:
        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # 检查列名
        expected_columns = ["单字拼音", "汉字", "词", "词拼音"]
        actual_columns = df.columns.tolist()
        
        print(f"检测到的列名: {actual_columns}")
        
        # 验证列名是否匹配
        if not all(col in actual_columns for col in expected_columns):
            print("警告: 列名不完全匹配，但将继续处理...")
            print(f"期望的列名: {expected_columns}")
            print(f"实际的列名: {actual_columns}")
        
        # 清理数据
        df = df.dropna()  # 删除空行
        
        # 转换为字典列表
        data_list = []
        for index, row in df.iterrows():
            item = {
                "单字拼音": str(row["单字拼音"]).strip() if pd.notna(row["单字拼音"]) else "",
                "汉字": str(row["汉字"]).strip() if pd.notna(row["汉字"]) else "",
                "词": str(row["词"]).strip() if pd.notna(row["词"]) else "",
                "词拼音": str(row["词拼音"]).strip() if pd.notna(row["词拼音"]) else ""
            }
            data_list.append(item)
        
        print(f"成功转换 {len(data_list)} 行数据")
        
        # 如果指定了输出文件路径，则保存到文件
        if output_file_path:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            print(f"JSON文件已保存到: {output_file_path}")
        
        return data_list
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {excel_file_path}")
        return []
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        return []

def preview_data(data_list: List[Dict[str, Any]], max_rows: int = 10):
    """
    预览转换后的数据
    
    Args:
        data_list: 数据列表
        max_rows: 最大显示行数
    """
    print(f"\n数据预览 (显示前{min(max_rows, len(data_list))}行):")
    print("-" * 60)
    
    for i, item in enumerate(data_list[:max_rows]):
        print(f"第{i+1}行:")
        for key, value in item.items():
            print(f"  {key}: {value}")
        print()

def main():
    """主函数"""
    print("Excel转JSON工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        # 如果没有命令行参数，提示用户输入
        excel_file = input("请输入Excel文件路径: ").strip()
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误: 文件 {excel_file} 不存在")
        return
    
    # 检查文件扩展名
    if not excel_file.lower().endswith(('.xlsx', '.xls')):
        print("警告: 文件扩展名不是.xlsx或.xls")
    
    # 生成输出文件名
    base_name = os.path.splitext(excel_file)[0]
    output_file = f"{base_name}.json"
    
    # 转换Excel为JSON
    data = excel_to_json(excel_file, output_file)
    
    if data:
        # 预览数据
        preview_data(data)
        
        # 显示统计信息
        print(f"转换完成!")
        print(f"总行数: {len(data)}")
        print(f"输出文件: {output_file}")
        
        # 显示一些统计信息
        unique_chars = set(item["汉字"] for item in data if item["汉字"])
        unique_words = set(item["词"] for item in data if item["词"])
        unique_pinyin = set(item["单字拼音"] for item in data if item["单字拼音"])
        
        print(f"唯一汉字数量: {len(unique_chars)}")
        print(f"唯一词汇数量: {len(unique_words)}")
        print(f"唯一单字拼音数量: {len(unique_pinyin)}")
        
        # 显示前几个汉字和拼音
        print(f"汉字示例: {list(unique_chars)[:10]}")
        print(f"拼音示例: {list(unique_pinyin)[:10]}")
        
    else:
        print("转换失败，没有生成数据")

if __name__ == "__main__":
    main()
