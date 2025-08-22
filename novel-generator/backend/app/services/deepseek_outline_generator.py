import json
from typing import Dict, List, Any
from .deepseek_client import DeepSeekClient

class DeepSeekOutlineGenerator:
    def __init__(self, api_key: str):
        self.client = DeepSeekClient(api_key)
    
    async def generate_outline(self, 
                        title: str, 
                        materials: List[Dict[str, Any]], 
                        chapter_count: int = 10,
                        required_words: List[str] = None) -> Dict[str, Any]:
        """使用DeepSeek API生成小说大纲"""
        
        # 构建材料信息
        material_info = self._format_materials(materials)
        
        # 如果没有指定必须字词，从材料中提取
        if not required_words:
            required_words = self._extract_required_words_from_materials(materials)
        
        # 构建必须用词的要求
        required_words_info = ""
        if required_words:
            required_words_info = f"""
5. **重要要求**：必须将以下字词合理分配到各个章节中，每个章节至少使用其中的一部分：
   必须使用的字词：{', '.join(required_words)}
   
   注意：
   - 这些字词需要自然地融入到章节的情节中
   - 不同章节可以使用不同的字词组合
   - 确保所有字词都被分配到某个章节中
"""
        
        prompt = f"""
请为小说《{title}》生成详细大纲，要求：

1. 总共{chapter_count}章
2. 每章都要有明确的标题和内容摘要
3. 整体情节要连贯，有起承转合
4. 需要融入以下创作材料：

{material_info}{required_words_info}

请按以下JSON格式返回大纲：
{{
    "title": "小说标题",
    "summary": "整体故事简介",
    "main_characters": [
        {{"name": "角色名", "description": "角色描述"}}
    ],
    "chapters": [
        {{
            "number": 1,
            "title": "章节标题",
            "summary": "章节内容摘要，包含主要情节和冲突",
            "key_events": ["关键事件1", "关键事件2"],
            "characters_involved": ["涉及角色"],
            "required_words": ["分配给此章节的必须字词"]
        }}
    ]
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的小说大纲创作助手，擅长构建完整的故事结构。请严格按照JSON格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat_completion(
                messages=messages,
                temperature=0.8,
                max_tokens=4000
            )
            
            if 'choices' in response and len(response['choices']) > 0:
                message = response['choices'][0]['message']
                content = message.get('content', '')
                reasoning_content = message.get('reasoning_content', '')
                
                # DeepSeek-reasoner模型优先使用reasoning_content
                final_content = content if content and content.strip() else reasoning_content
                
                if final_content:
                    # 尝试解析JSON
                    try:
                        # 提取JSON部分（可能包含在代码块中）
                        json_text = self._extract_json(final_content)
                        outline_data = json.loads(json_text)
                        
                        # 验证大纲结构
                        if self._validate_outline(outline_data, chapter_count):
                            # 如果有必须用词，验证和补充分配
                            if required_words:
                                outline_data = self._ensure_words_distribution(outline_data, required_words)
                            print(f"✅ 成功生成{chapter_count}章大纲")
                            return outline_data
                        else:
                            print("⚠️ 生成的大纲结构不完整，使用备用方案")
                            return self._create_fallback_outline(title, chapter_count)
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析失败: {e}")
                        print(f"原始内容: {final_content[:500]}...")
                        return self._create_fallback_outline(title, chapter_count)
                else:
                    print("⚠️ API返回空内容")
                    return self._create_fallback_outline(title, chapter_count)
            else:
                print("⚠️ API响应格式错误")
                return self._create_fallback_outline(title, chapter_count)
                
        except Exception as e:
            print(f"❌ 生成大纲时出错: {e}")
            return self._create_fallback_outline(title, chapter_count)
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON部分"""
        # 尝试找到JSON代码块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        # 尝试找到花括号包围的内容
        start = text.find("{")
        if start != -1:
            # 找到最后一个}
            end = text.rfind("}")
            if end != -1 and end > start:
                return text[start:end+1]
        
        return text
    
    def _validate_outline(self, outline_data: Dict[str, Any], expected_chapters: int) -> bool:
        """验证大纲结构是否完整"""
        required_fields = ["title", "summary", "main_characters", "chapters"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in outline_data:
                print(f"❌ 缺少字段: {field}")
                return False
        
        # 检查章节数量
        chapters = outline_data.get("chapters", [])
        if len(chapters) != expected_chapters:
            print(f"❌ 章节数量不匹配: 期望{expected_chapters}，实际{len(chapters)}")
            return False
        
        # 检查每个章节的结构
        for i, chapter in enumerate(chapters):
            required_chapter_fields = ["number", "title", "summary"]
            for field in required_chapter_fields:
                if field not in chapter:
                    print(f"❌ 第{i+1}章缺少字段: {field}")
                    return False
        
        return True
    
    def _format_materials(self, materials: List[Dict[str, Any]]) -> str:
        """格式化材料信息"""
        if not materials:
            return "无特定创作材料"
        
        formatted = []
        for material in materials:
            formatted.append(f"""
类型：{material.get('category', '未知')}
创作指导：
- 世界构建：{material.get('writing_guidelines', {}).get('world_building', '无')}
- 角色发展：{material.get('writing_guidelines', {}).get('character_development', '无')}
- 情节发展：{material.get('writing_guidelines', {}).get('plot_development', '无')}
- 语言风格：{material.get('writing_guidelines', {}).get('language_style', '无')}
""")
        
        return "\n".join(formatted)
    
    def _extract_required_words_from_materials(self, materials: List[Dict[str, Any]]) -> List[str]:
        """从材料中提取必须使用的字词"""
        required_words = []
        
        for material in materials:
            required_characters = material.get('required_characters', [])
            for char_info in required_characters:
                if isinstance(char_info, dict) and 'character' in char_info:
                    required_words.append(char_info['character'])
                elif isinstance(char_info, str):
                    required_words.append(char_info)
        
        return list(set(required_words))  # 去重
    
    def _ensure_words_distribution(self, outline_data: Dict[str, Any], required_words: List[str]) -> Dict[str, Any]:
        """确保所有必须用词都被分配到章节中"""
        chapters = outline_data.get("chapters", [])
        
        # 收集已分配的字词
        assigned_words = set()
        for chapter in chapters:
            chapter_words = chapter.get("required_words", [])
            assigned_words.update(chapter_words)
        
        # 找出未分配的字词
        unassigned_words = [word for word in required_words if word not in assigned_words]
        
        if unassigned_words:
            print(f"⚠️ 发现未分配的字词: {unassigned_words}")
            # 将未分配的字词平均分配到各章节
            words_per_chapter = len(unassigned_words) // len(chapters)
            remaining_words = len(unassigned_words) % len(chapters)
            
            word_index = 0
            for i, chapter in enumerate(chapters):
                if "required_words" not in chapter:
                    chapter["required_words"] = []
                
                # 分配基本数量的字词
                words_to_add = words_per_chapter
                # 前几章多分配一个字词（处理余数）
                if i < remaining_words:
                    words_to_add += 1
                
                # 添加字词到章节
                for j in range(words_to_add):
                    if word_index < len(unassigned_words):
                        chapter["required_words"].append(unassigned_words[word_index])
                        word_index += 1
            
            print(f"✅ 已将未分配字词重新分配到各章节")
        
        # 验证分配结果
        total_assigned = set()
        for chapter in chapters:
            chapter_words = chapter.get("required_words", [])
            total_assigned.update(chapter_words)
        
        missing_words = [word for word in required_words if word not in total_assigned]
        if missing_words:
            print(f"⚠️ 仍有字词未分配: {missing_words}")
        else:
            print(f"✅ 所有{len(required_words)}个必须字词已成功分配")
        
        return outline_data
    
    def _create_fallback_outline(self, title: str, chapter_count: int) -> Dict[str, Any]:
        """创建备用大纲结构"""
        chapters = []
        for i in range(1, chapter_count + 1):
            chapters.append({
                "number": i,
                "title": f"第{i}章",
                "summary": f"第{i}章的内容概要",
                "key_events": [f"事件{i}"],
                "characters_involved": ["主角"]
            })
        
        return {
            "title": title,
            "summary": "一个精彩的故事",
            "main_characters": [{"name": "主角", "description": "故事的主人公"}],
            "chapters": chapters
        }
