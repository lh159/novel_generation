#!/usr/bin/env python3
"""
测试章节式小说生成API
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/novels-v2"

async def test_chapter_novel_api():
    """测试章节式小说API的完整流程"""
    
    async with httpx.AsyncClient() as client:
        print("=== 章节式小说生成API测试 ===\n")
        
        # 1. 创建新小说
        print("1. 创建新小说...")
        novel_data = {
            "title": "测试章节小说",
            "chapter_count": 3,
            "material_ids": []
        }
        
        response = await client.post(f"{BASE_URL}/", json=novel_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            novel = response.json()
            print(f"创建成功！小说ID: {novel['id']}")
            print(f"标题: {novel['title']}")
            print(f"总章节数: {novel['total_chapters']}")
            print(f"状态: {novel['status']}")
            novel_id = novel['id']
        else:
            print(f"创建失败: {response.text}")
            return
        
        print("\n" + "="*50 + "\n")
        
        # 2. 生成大纲
        print("2. 生成小说大纲...")
        response = await client.post(f"{BASE_URL}/{novel_id}/outline", json=[])
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("大纲生成成功！")
            print(f"消息: {result['message']}")
            outline = result['outline']
            print(f"小说简介: {outline.get('summary', '无')}")
            print("章节列表:")
            for chapter in outline.get('chapters', []):
                print(f"  第{chapter['number']}章: {chapter['title']}")
                print(f"    摘要: {chapter['summary']}")
        else:
            print(f"大纲生成失败: {response.text}")
            return
        
        print("\n" + "="*50 + "\n")
        
        # 3. 获取大纲
        print("3. 获取小说大纲...")
        response = await client.get(f"{BASE_URL}/{novel_id}/outline")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            outline = response.json()
            print("获取大纲成功！")
            print(f"标题: {outline['title']}")
            print(f"章节数量: {len(outline['chapters'])}")
        else:
            print(f"获取大纲失败: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # 4. 生成第一章
        print("4. 生成第一章...")
        chapter_data = {
            "target_length": 1500
        }
        
        response = await client.post(
            f"{BASE_URL}/{novel_id}/chapters/1/generate",
            json=chapter_data,
            params={"material_ids": []}
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("第一章生成成功！")
            print(f"消息: {result['message']}")
            chapter = result['chapter']
            print(f"章节标题: {chapter['title']}")
            print(f"字数: {chapter['word_count']}")
            print(f"状态: {chapter['status']}")
            print(f"内容预览: {chapter['content'][:200]}...")
        else:
            print(f"第一章生成失败: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # 5. 获取章节列表
        print("5. 获取章节列表...")
        response = await client.get(f"{BASE_URL}/{novel_id}/chapters")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            chapters = response.json()
            print(f"获取章节列表成功！共{len(chapters)}章")
            for chapter in chapters:
                print(f"  第{chapter['chapter_number']}章: {chapter['title']} ({chapter['status']})")
                if chapter['word_count'] > 0:
                    print(f"    字数: {chapter['word_count']}")
        else:
            print(f"获取章节列表失败: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # 6. 获取小说信息
        print("6. 获取小说信息...")
        response = await client.get(f"{BASE_URL}/{novel_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            novel = response.json()
            print("获取小说信息成功！")
            print(f"标题: {novel['title']}")
            print(f"总章节数: {novel['total_chapters']}")
            print(f"已完成章节数: {novel['completed_chapters']}")
            print(f"状态: {novel['status']}")
        else:
            print(f"获取小说信息失败: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # 7. 获取小说列表
        print("7. 获取小说列表...")
        response = await client.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            novels = response.json()
            print(f"获取小说列表成功！共{len(novels)}部小说")
            for novel in novels:
                print(f"  - {novel['title']} ({novel['status']}) - {novel['completed_chapters']}/{novel['total_chapters']}章")
        else:
            print(f"获取小说列表失败: {response.text}")
        
        print("\n" + "="*50 + "\n")
        print("测试完成！")

if __name__ == "__main__":
    asyncio.run(test_chapter_novel_api())
