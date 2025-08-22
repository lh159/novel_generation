#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说类别拼音分配脚本
按照小说类别随机分配单字拼音汉字对应表
"""

import json
import random
import math

# 小说类别定义
NOVEL_CATEGORIES = [
    {
        "name": "东方玄幻",
        "examples": "苟在初圣魔门当人材、夜无疆"
    },
    {
        "name": "异世大陆", 
        "examples": "诡秘之主、元始法则"
    },
    {
        "name": "王朝争霸",
        "examples": "江山美人志、天珠变"
    },
    {
        "name": "高武世界",
        "examples": "别人练级我修仙，苟到大乘再出山、沧元图"
    },
    {
        "name": "现代魔法",
        "examples": "琴帝、冰火魔厨"
    },
    {
        "name": "剑与魔法",
        "examples": "盘龙、巫师之旅、王国血脉"
    },
    {
        "name": "史诗奇幻",
        "examples": "放开那个女巫、登神之前，做个好领主"
    },
    {
        "name": "神秘幻想",
        "examples": "蒸汽朋克下的神秘世界、异界之死灵法师"
    },
    {
        "name": "历史神话",
        "examples": "洪荒历、我乃路易十四、吞噬世界之龙"
    },
    {
        "name": "另类幻想",
        "examples": "黑石密码、重生支配者、队里最强的都会死"
    },
    {
        "name": "传统武侠",
        "examples": "血染侠衣、侠徒幻世录"
    },
    {
        "name": "武侠幻想",
        "examples": "九鼎记、盖世双谐、剑出大唐"
    },
    {
        "name": "国术无双",
        "examples": "无敌黑拳、白目老师、我有一块属性板"
    },
    {
        "name": "古武未来",
        "examples": "我有一刀在手、武入魔途、我成了武侠乐园的NPC"
    },
    {
        "name": "武侠同人",
        "examples": "武侠：从六扇门开始模拟人生、我慕容复只想复国、从柯镇恶开始逆天改命"
    },
    {
        "name": "修真文明",
        "examples": "长生从炼丹宗师开始、三寸人间、祖宗祭天，全族升仙"
    },
    {
        "name": "幻想修仙",
        "examples": "仙人消失之后、从赘婿开始建立长生家族、凡人修仙传"
    },
    {
        "name": "现代修真",
        "examples": "大数据修仙、天下第九"
    },
    {
        "name": "神话修真",
        "examples": "凡人修仙之仙界篇、巫风"
    },
    {
        "name": "古典仙侠",
        "examples": "青葫剑仙、飞剑问道"
    },
    {
        "name": "都市生活",
        "examples": "那年花开1981、刑警日志"
    },
    {
        "name": "都市异能",
        "examples": "偷来的仙术有点神、全球高武、我真的长生不老"
    },
    {
        "name": "异术超能",
        "examples": "捞尸人、深空彼岸、龙王的傲娇日常"
    },
    {
        "name": "青春校园",
        "examples": "重生似水青春、重燃2001"
    },
    {
        "name": "娱乐明星",
        "examples": "从电影抽取技能、娱乐圈第一深情？我可是海这个明星很想退休"
    },
    {
        "name": "商战职场",
        "examples": "赏金猎手、覆手、国民法医"
    },
    {
        "name": "时代叙事",
        "examples": "奔腾年代——向南向北、我的1979"
    },
    {
        "name": "家庭伦理",
        "examples": "男人都是孩子、我的女儿之我的天使、带着爸妈去上班"
    },
    {
        "name": "军旅生涯",
        "examples": "从我是特种兵开始打卡、特种岁月"
    },
    {
        "name": "军事战争",
        "examples": "炮火弧线、大国军舰"
    },
    {
        "name": "战争幻想",
        "examples": "末日之最终战争、最强之军火商人"
    },
    {
        "name": "抗战烽火",
        "examples": "我在亮剑当战狼、从八百开始崛起"
    },
    {
        "name": "谍战特工",
        "examples": "我的谍战岁月、谍影风云"
    },
    {
        "name": "架空历史",
        "examples": "庆余年、赘婿、极品家丁"
    },
    {
        "name": "秦汉三国",
        "examples": "大秦：不装了，你爹我是秦始皇、神话版三国、三国：开局误认吕布为岳父"
    },
    {
        "name": "唐宋元明",
        "examples": "大明国师、回到明朝当王爷、穿越武大郎从卖饼开始、挟明"
    },
    {
        "name": "外国历史",
        "examples": "美利坚1881：西部传奇、神圣罗马帝国"
    },
    {
        "name": "电子竞技",
        "examples": "王者时刻、英雄联盟：我的时代"
    },
    {
        "name": "虚拟网游",
        "examples": "全职高手、从零开始"
    },
    {
        "name": "游戏异界",
        "examples": "超神机械师、暗黑破坏神之毁灭"
    },
    {
        "name": "篮球运动",
        "examples": "我真的只是想打铁、篮坛教皇"
    },
    {
        "name": "足球运动",
        "examples": "我们是冠军、禁区之狐"
    },
    {
        "name": "时空穿梭",
        "examples": "黎明之剑、异常生物见闻录"
    },
    {
        "name": "未来世界",
        "examples": "吞噬星空、未来天王"
    },
    {
        "name": "超级科技",
        "examples": "学霸的黑科技系统、机武风暴"
    },
    {
        "name": "进化变异",
        "examples": "灵境行者、九星毒奶"
    },
    {
        "name": "无限流",
        "examples": "无限恐怖、这个主神空间怎么是缝合怪啊！"
    },
    {
        "name": "侦探推理",
        "examples": "我有一座冒险屋、缺陷异世界"
    },
    {
        "name": "诡秘悬疑",
        "examples": "神秘复苏、镇妖博物馆"
    },
    {
        "name": "探险生存",
        "examples": "鬼吹灯、天师联盟之净心咒"
    }
]

def read_pinyin_chars_table(file_path: str):
    """读取单字拼音汉字对应表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        pinyin_chars_list = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('单字拼音汉字对应表') and not line.startswith('=') and not line.startswith('总计'):
                # 解析格式: "001. biàn → 遍 (1个汉字)"
                if ' → ' in line:
                    parts = line.split(' → ')
                    if len(parts) == 2:
                        pinyin_part = parts[0].split('. ')[1] if '. ' in parts[0] else parts[0]
                        char_part = parts[1].split(' (')[0] if ' (' in parts[1] else parts[1]
                        pinyin_chars_list.append({
                            "pinyin": pinyin_part.strip(),
                            "char": char_part.strip()
                        })
        
        return pinyin_chars_list
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return []

def divide_pinyin_chars_random(pinyin_chars_list: list, num_categories: int = 50):
    """将拼音汉字列表随机平均分为指定数量的类别"""
    total_items = len(pinyin_chars_list)
    
    # 复制列表并随机打乱
    shuffled_list = pinyin_chars_list.copy()
    random.shuffle(shuffled_list)
    
    # 计算每类应该包含的项目数量
    items_per_category = math.ceil(total_items / num_categories)
    
    categories = []
    for i in range(num_categories):
        start_idx = i * items_per_category
        end_idx = min((i + 1) * items_per_category, total_items)
        
        if start_idx < total_items:
            category_items = shuffled_list[start_idx:end_idx]
            categories.append({
                "category_num": i + 1,
                "novel_category": NOVEL_CATEGORIES[i],
                "pinyin_chars": category_items,
                "count": len(category_items)
            })
    
    return categories

def generate_category_report(categories: list, output_file: str):
    """生成分类报告"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 小说类别拼音汉字分配报告\n\n")
            f.write("## 概述\n\n")
            f.write("本报告将1252个单字拼音汉字对应关系随机平均分为50个小说类别。\n\n")
            f.write("**注意**: 本次分配采用随机抽取方式，确保每类都能获得随机分布的拼音汉字。\n\n")
            
            # 统计信息
            total_items = sum(category["count"] for category in categories)
            f.write(f"**总拼音汉字对数**: {total_items}\n")
            f.write(f"**小说类别数**: {len(categories)}\n")
            f.write(f"**平均每类数量**: {total_items // len(categories)}\n\n")
            
            # 分类详情
            f.write("## 分类详情\n\n")
            
            for category in categories:
                novel_category = category["novel_category"]
                f.write(f"### 第{category['category_num']:02d}类: {novel_category['name']}\n\n")
                f.write(f"**示例小说**: {novel_category['examples']}\n\n")
                f.write(f"**拼音汉字对数**: {category['count']}个\n\n")
                
                # 拼音汉字列表
                f.write("**拼音汉字对应表**:\n")
                f.write("```\n")
                for i, item in enumerate(category["pinyin_chars"], 1):
                    f.write(f"{i:03d}. {item['pinyin']} → {item['char']}\n")
                f.write("```\n\n")
                
                f.write("---\n\n")
            
            # 生成纯分类文件
            pure_file = "小说类别拼音汉字分配表.txt"
            with open(pure_file, 'w', encoding='utf-8') as pure_f:
                pure_f.write("小说类别拼音汉字分配表\n")
                pure_f.write("=" * 80 + "\n\n")
                pure_f.write("注意: 本次分配采用随机抽取方式，确保每类都能获得随机分布的拼音汉字。\n\n")
                
                for category in categories:
                    novel_category = category["novel_category"]
                    pure_f.write(f"第{category['category_num']:02d}类: {novel_category['name']}\n")
                    pure_f.write(f"示例小说: {novel_category['examples']}\n")
                    pure_f.write(f"拼音汉字对数: {category['count']}个\n")
                    pure_f.write("-" * 50 + "\n")
                    
                    for i, item in enumerate(category["pinyin_chars"], 1):
                        pure_f.write(f"{i:03d}. {item['pinyin']} → {item['char']}\n")
                    
                    pure_f.write("\n" + "=" * 80 + "\n\n")
            
            print(f"分类报告已保存到: {output_file}")
            print(f"纯分类文件已保存到: {pure_file}")
            
    except Exception as e:
        print(f"生成报告时发生错误: {str(e)}")

def generate_json_output(categories: list, output_file: str):
    """生成JSON格式的输出文件"""
    try:
        # 转换为列表格式，便于使用
        categories_list = []
        for category in categories:
            novel_category = category["novel_category"]
            categories_list.append({
                "category_num": category["category_num"],
                "category_name": novel_category["name"],
                "examples": novel_category["examples"],
                "pinyin_chars": category["pinyin_chars"],
                "count": category["count"]
            })
        
        # 保存为JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(categories_list, f, ensure_ascii=False, indent=2)
        
        print(f"JSON格式输出已保存到: {output_file}")
        
    except Exception as e:
        print(f"生成JSON文件时发生错误: {str(e)}")

def main():
    """主函数"""
    input_file = "单字拼音汉字对应表.txt"
    output_file = "小说类别拼音汉字分配报告.md"
    json_output_file = "小说类别拼音汉字分配表.json"
    
    print("开始读取单字拼音汉字对应表...")
    
    # 读取拼音汉字对应表
    pinyin_chars_list = read_pinyin_chars_table(input_file)
    
    if pinyin_chars_list:
        print(f"成功读取 {len(pinyin_chars_list)} 个拼音汉字对应关系")
        
        # 设置随机种子，确保结果可重现（可选）
        random.seed(42)  # 可以注释掉这行来获得完全随机的结果
        
        # 随机分类
        print("开始随机分类...")
        categories = divide_pinyin_chars_random(pinyin_chars_list, 50)
        
        print(f"成功随机分为 {len(categories)} 类")
        for category in categories:
            novel_category = category["novel_category"]
            print(f"第{category['category_num']:02d}类({novel_category['name']}): {category['count']}个拼音汉字对")
        
        # 生成报告
        print("生成分类报告...")
        generate_category_report(categories, output_file)
        
        # 生成JSON输出
        print("生成JSON格式输出...")
        generate_json_output(categories, json_output_file)
        
        # 显示一些示例
        print("\n示例分类:")
        count = 0
        for category in categories:
            if count < 3:  # 只显示前3个
                novel_category = category["novel_category"]
                print(f"  {novel_category['name']}: {category['count']}个拼音汉字对")
                if category["pinyin_chars"]:
                    sample = category["pinyin_chars"][0]
                    print(f"    示例: {sample['pinyin']} → {sample['char']}")
                count += 1
            else:
                break
        
    else:
        print("读取拼音汉字对应表失败")

if __name__ == "__main__":
    main()
