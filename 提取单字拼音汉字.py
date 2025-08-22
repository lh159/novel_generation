#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取单字拼音汉字脚本
从JSON文件中提取单字拼音和对应的汉字
"""

import json
from collections import defaultdict

def extract_pinyin_chars(json_file_path: str):
    """
    从JSON文件中提取单字拼音和对应汉字
    
    Args:
        json_file_path: JSON文件路径
    
    Returns:
        拼音汉字对应关系字典
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 统计信息
        total_entries = len(data)
        unique_pinyin = set()
        pinyin_to_chars = defaultdict(list)
        
        # 提取数据
        for entry in data:
            pinyin = entry.get("单字拼音", "").strip()
            char = entry.get("汉字", "").strip()
            
            if pinyin and char:
                unique_pinyin.add(pinyin)
                pinyin_to_chars[pinyin].append(char)
        
        return {
            "total_entries": total_entries,
            "unique_pinyin_count": len(unique_pinyin),
            "pinyin_to_chars": dict(pinyin_to_chars)
        }
        
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def generate_pinyin_chars_report(pinyin_data: dict, output_file: str):
    """
    生成拼音汉字对应关系报告
    
    Args:
        pinyin_data: 拼音数据字典
        output_file: 输出文件路径
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 单字拼音汉字对应关系报告\n\n")
            
            # 统计信息
            f.write("## 统计信息\n\n")
            f.write(f"- **总条目数**: {pinyin_data['total_entries']}\n")
            f.write(f"- **唯一单字拼音数**: {pinyin_data['unique_pinyin_count']}\n\n")
            
            # 按拼音排序的完整列表
            f.write("## 单字拼音汉字对应表\n\n")
            f.write("| 序号 | 单字拼音 | 对应汉字 | 汉字数量 |\n")
            f.write("|------|----------|----------|----------|\n")
            
            for i, pinyin in enumerate(sorted(pinyin_data['pinyin_to_chars'].keys()), 1):
                chars = pinyin_data['pinyin_to_chars'][pinyin]
                char_str = "、".join(chars)
                
                f.write(f"| {i:03d} | {pinyin} | {char_str} | {len(chars)}个 |\n")
            
            # 生成纯拼音汉字对应文件
            pure_file = "单字拼音汉字对应表.txt"
            with open(pure_file, 'w', encoding='utf-8') as pure_f:
                pure_f.write("单字拼音汉字对应表\n")
                pure_f.write("=" * 50 + "\n\n")
                
                for i, pinyin in enumerate(sorted(pinyin_data['pinyin_to_chars'].keys()), 1):
                    chars = pinyin_data['pinyin_to_chars'][pinyin]
                    char_str = "、".join(chars)
                    
                    pure_f.write(f"{i:03d}. {pinyin} → {char_str} ({len(chars)}个汉字)\n")
                
                pure_f.write(f"\n总计: {pinyin_data['unique_pinyin_count']}个单字拼音")
            
            # 生成纯拼音列表文件
            pinyin_only_file = "单字拼音列表.txt"
            with open(pinyin_only_file, 'w', encoding='utf-8') as pinyin_f:
                pinyin_f.write("单字拼音列表\n")
                pinyin_f.write("=" * 50 + "\n\n")
                for pinyin in sorted(pinyin_data['pinyin_to_chars'].keys()):
                    pinyin_f.write(f"{pinyin}\n")
            
            # 生成纯汉字列表文件
            chars_only_file = "单字汉字列表.txt"
            with open(chars_only_file, 'w', encoding='utf-8') as chars_f:
                chars_f.write("单字汉字列表\n")
                chars_f.write("=" * 50 + "\n\n")
                all_chars = set()
                for chars in pinyin_data['pinyin_to_chars'].values():
                    all_chars.update(chars)
                
                for char in sorted(all_chars):
                    chars_f.write(f"{char}\n")
                
                chars_f.write(f"\n总计: {len(all_chars)}个汉字")
            
            print(f"拼音汉字对应关系报告已保存到: {output_file}")
            print(f"纯拼音汉字对应表已保存到: {pure_file}")
            print(f"纯拼音列表已保存到: {pinyin_only_file}")
            print(f"纯汉字列表已保存到: {chars_only_file}")
            
    except Exception as e:
        print(f"生成报告时发生错误: {str(e)}")

def generate_json_output(pinyin_data: dict, output_file: str):
    """
    生成JSON格式的输出文件
    
    Args:
        pinyin_data: 拼音数据字典
        output_file: 输出文件路径
    """
    try:
        # 转换为列表格式，便于使用
        pinyin_chars_list = []
        for pinyin, chars in sorted(pinyin_data['pinyin_to_chars'].items()):
            pinyin_chars_list.append({
                "单字拼音": pinyin,
                "对应汉字": chars,
                "汉字数量": len(chars)
            })
        
        # 保存为JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pinyin_chars_list, f, ensure_ascii=False, indent=2)
        
        print(f"JSON格式输出已保存到: {output_file}")
        
    except Exception as e:
        print(f"生成JSON文件时发生错误: {str(e)}")

def main():
    """主函数"""
    json_file = "副本常用字词拼音-终稿.json"
    output_file = "单字拼音汉字对应关系报告.md"
    json_output_file = "单字拼音汉字对应表.json"
    
    print("开始读取JSON文件...")
    
    # 提取数据
    pinyin_data = extract_pinyin_chars(json_file)
    
    if pinyin_data:
        print(f"成功提取数据:")
        print(f"- 总条目数: {pinyin_data['total_entries']}")
        print(f"- 唯一单字拼音数: {pinyin_data['unique_pinyin_count']}")
        
        # 生成报告
        print("生成拼音汉字对应关系报告...")
        generate_pinyin_chars_report(pinyin_data, output_file)
        
        # 生成JSON输出
        print("生成JSON格式输出...")
        generate_json_output(pinyin_data, json_output_file)
        
        # 显示一些示例
        print("\n示例拼音汉字对应关系:")
        count = 0
        for pinyin, chars in sorted(pinyin_data['pinyin_to_chars'].items()):
            if count < 5:  # 只显示前5个
                print(f"  {pinyin} → {', '.join(chars)}")
                count += 1
            else:
                break
        
    else:
        print("数据提取失败")

if __name__ == "__main__":
    main()
