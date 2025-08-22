#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 测试引号检测
content_preview = """# 第一章：霓虹深渊

雨水混杂着霓虹灯光，在潮湿的巷道上折射出迷离的光晕。凯拉高外套领口，快步穿过第七区错综复杂的小巷，神经接口微微发烫——维克多的紧急通讯已经响了三次。

"你迟到了，凯。"

维克多的全息投影在凯的视网膜上闪烁，老人的虚拟影像被数据流干扰得断断续续。

"暴雨导致磁悬浮线路瘫痪，"凯低声回应，同时警惕地扫视着周围环境，"你知道新港市的交通系统有多不可靠。"

"借口不会让委托人开心，也不会让你的账户多一个信用点。"维克多的投影晃动着，"黑曜石大厦，47层，标准数据窃取任务。委托人要的是奥米茄集团金融部门的交易记录，老规矩，我抽30%。"""

print("章节内容预览:")
print(content_preview)
print()

print("引号分析:")
print(f'英文引号 ": {content_preview.count('"')} 个')
print(f'中文左引号 ": {content_preview.count('"')} 个')  
print(f'中文右引号 ": {content_preview.count('"')} 个')

print()
print("包含引号的行:")
lines = content_preview.split('\n')
for i, line in enumerate(lines):
    if '"' in line or '"' in line or '"' in line:
        print(f'{i+1}: {line}')

print()
print("测试检测逻辑:")
test_texts = [
    '"你迟到了，凯。"',
    '"暴雨导致磁悬浮线路瘫痪，"凯低声回应',
    '维克多的全息投影在凯的视网膜上闪烁',
    '"借口不会让委托人开心，也不会让你的账户多一个信用点。"维克多的投影晃动着'
]

for text in test_texts:
    has_quotes = '"' in text or '"' in text or '"' in text
    print(f'文本: {text[:50]}...')
    print(f'包含引号: {has_quotes}')
    print()
