import openai
from typing import Dict, List, Any
import json

class OutlineGenerator:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_outline(self, 
                        title: str, 
                        materials: List[Dict[str, Any]], 
                        chapter_count: int = 10) -> Dict[str, Any]:
        """生成小说大纲"""
        
        # 构建材料信息
        material_info = self._format_materials(materials)
        
        prompt = f"""
请为小说《{title}》生成详细大纲，要求：

1. 总共{chapter_count}章
2. 每章都要有明确的标题和内容摘要
3. 整体情节要连贯，有起承转合
4. 需要融入以下创作材料：

{material_info}

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
            "characters_involved": ["涉及角色"]
        }}
    ]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的小说大纲创作助手，擅长构建完整的故事结构。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            # 尝试解析JSON
            try:
                outline_data = json.loads(content)
                return outline_data
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基础结构
                return self._create_fallback_outline(title, chapter_count)
                
        except Exception as e:
            print(f"生成大纲时出错: {e}")
            return self._create_fallback_outline(title, chapter_count)
    
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
