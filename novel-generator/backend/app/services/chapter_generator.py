import openai
from typing import Dict, List, Any, Optional
import json

class ChapterGenerator:
    def __init__(self, api_key: str):
        # 使用DeepSeek API端点
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
    
    def generate_chapter(self, 
                        novel_title: str,
                        chapter_info: Dict[str, Any],
                        previous_chapters: List[str],
                        materials: List[Dict[str, Any]],
                        target_length: int = 2000) -> Dict[str, Any]:
        """生成单个章节内容"""
        
        # 构建上下文
        context = self._build_context(novel_title, chapter_info, previous_chapters, materials)
        
        # 获取必须用到的字（优先使用章节指定的，否则从材料中提取）
        required_words = chapter_info.get('required_words', [])
        if not required_words:
            all_required_words = self._extract_required_words_from_materials(materials)
            # 如果材料中有必须字词，为这个章节分配一部分
            if all_required_words:
                chapter_num = chapter_info.get('number', 1)
                words_per_chapter = max(1, len(all_required_words) // 10)  # 假设10章，平均分配
                start_idx = (chapter_num - 1) * words_per_chapter
                end_idx = start_idx + words_per_chapter
                required_words = all_required_words[start_idx:end_idx]
        
        required_words_text = ""
        if required_words:
            required_words_text = f"""
- **必须使用的字词**：{', '.join(required_words)}
  注意：这些字词必须在章节中自然地出现，不能生硬插入，要融入情节和对话中"""
        
        prompt = f"""
请为小说《{novel_title}》写第{chapter_info['number']}章：《{chapter_info['title']}》

章节要求：
- 字数约{target_length}字
- 根据大纲摘要展开：{chapter_info['summary']}
- 包含关键事件：{', '.join(chapter_info.get('key_events', []))}
- 涉及角色：{', '.join(chapter_info.get('characters_involved', []))}{required_words_text}

上下文信息：
{context}

请直接返回章节内容，要求：
1. 情节生动有趣，符合大纲设定
2. 人物对话自然
3. 描写细致入微
4. 与前面章节保持连贯性
5. 融入创作材料的风格特点
6. 必须自然地使用指定的字词，不能生硬插入

**【重要格式要求】**：
7. 对话部分必须按以下格式标记：
   - 旁白和叙述部分：在段落开头标注"正文："
   - 主角说话：标注"主角："后跟对话内容
   - 其他角色说话：标注"角色名："或"其他角色："后跟对话内容
   
示例格式：
正文：雨水混杂着霓虹灯光，在潮湿的巷道上折射出迷离的光晕。
主角：你迟到了，这次的任务很重要。
其他角色：抱歉，路上遇到了一些麻烦。
正文：他看向远处的大楼，心中涌起不安的预感。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的小说作家，擅长写作各种类型的小说章节。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            word_count = len(content)
            
            # 验证必须用到的字是否都包含在内容中
            required_words = chapter_info.get('required_words', [])
            used_words = []
            missing_words = []
            
            if required_words:
                for word in required_words:
                    if word in content:
                        used_words.append(word)
                    else:
                        missing_words.append(word)
            
            return {
                "content": content,
                "word_count": word_count,
                "status": "completed",
                "required_words": required_words,
                "used_words": used_words,
                "missing_words": missing_words,
                "words_completion_rate": len(used_words) / len(required_words) if required_words else 1.0
            }
                
        except Exception as e:
            print(f"生成章节时出错: {e}")
            return {
                "content": f"第{chapter_info['number']}章内容生成失败，请重试。",
                "word_count": 0,
                "status": "failed"
            }
    
    def _build_context(self, 
                      novel_title: str,
                      chapter_info: Dict[str, Any], 
                      previous_chapters: List[str],
                      materials: List[Dict[str, Any]]) -> str:
        """构建章节生成的上下文"""
        
        context_parts = []
        
        # 添加创作材料信息
        if materials:
            material_context = "创作风格指导：\n"
            for material in materials:
                guidelines = material.get('writing_guidelines', {})
                material_context += f"- 世界观：{guidelines.get('world_building', '')}\n"
                material_context += f"- 角色设定：{guidelines.get('character_development', '')}\n"
                material_context += f"- 语言风格：{guidelines.get('language_style', '')}\n"
            context_parts.append(material_context)
        
        # 添加前面章节的摘要（最多3章）
        if previous_chapters:
            recent_chapters = previous_chapters[-3:]  # 只取最近3章
            chapter_context = "前面章节概要：\n"
            for i, chapter_content in enumerate(recent_chapters, 1):
                # 截取章节开头作为摘要
                summary = chapter_content[:200] + "..." if len(chapter_content) > 200 else chapter_content
                chapter_context += f"第{len(previous_chapters) - len(recent_chapters) + i}章：{summary}\n\n"
            context_parts.append(chapter_context)
        
        return "\n".join(context_parts)
    
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
    
    def generate_chapter_with_dialogue(self, 
                                     novel_title: str,
                                     chapter_info: Dict[str, Any],
                                     previous_chapters: List[str],
                                     materials: List[Dict[str, Any]],
                                     dialogue_context: Optional[Dict[str, Any]] = None,
                                     target_length: int = 2000) -> Dict[str, Any]:
        """生成包含对话交互的章节"""
        
        base_result = self.generate_chapter(novel_title, chapter_info, previous_chapters, materials, target_length)
        
        if dialogue_context:
            # 如果有对话上下文，可以在这里添加特殊处理
            # 例如：确保主角的行为符合用户的选择
            pass
        
        return base_result
    
    def regenerate_chapter_with_missing_words(self, 
                                            novel_title: str,
                                            chapter_info: Dict[str, Any],
                                            previous_chapters: List[str],
                                            materials: List[Dict[str, Any]],
                                            missing_words: List[str],
                                            previous_content: str,
                                            target_length: int = 2000) -> Dict[str, Any]:
        """重新生成章节，重点强调缺失的必须字词"""
        
        # 构建上下文
        context = self._build_context(novel_title, chapter_info, previous_chapters, materials)
        
        prompt = f"""
请为小说《{novel_title}》重新写第{chapter_info['number']}章：《{chapter_info['title']}》

之前生成的内容缺少了一些必须使用的字词，请重新创作。

章节要求：
- 字数约{target_length}字
- 根据大纲摘要展开：{chapter_info['summary']}
- 包含关键事件：{', '.join(chapter_info.get('key_events', []))}
- 涉及角色：{', '.join(chapter_info.get('characters_involved', []))}
- **必须使用这些缺失的字词**：{', '.join(missing_words)}
- 全部必须使用的字词：{', '.join(chapter_info.get('required_words', []))}

上下文信息：
{context}

之前的内容参考（请重新创作，不要直接复制）：
{previous_content[:500]}...

请直接返回章节内容，要求：
1. 情节生动有趣，符合大纲设定
2. 人物对话自然
3. 描写细致入微
4. 与前面章节保持连贯性
5. 融入创作材料的风格特点
6. **特别注意：必须自然地使用所有指定的字词，尤其是缺失的字词：{', '.join(missing_words)}**
7. 不能生硬插入字词，要融入情节和对话中

**【重要格式要求】**：
8. 对话部分必须按以下格式标记：
   - 旁白和叙述部分：在段落开头标注"正文："
   - 主角说话：标注"主角："后跟对话内容
   - 其他角色说话：标注"角色名："或"其他角色："后跟对话内容
   
示例格式：
正文：雨水混杂着霓虹灯光，在潮湿的巷道上折射出迷离的光晕。
主角：你迟到了，这次的任务很重要。
其他角色：抱歉，路上遇到了一些麻烦。
正文：他看向远处的大楼，心中涌起不安的预感。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的小说作家，擅长写作各种类型的小说章节。你特别擅长在保持故事流畅性的同时，自然地融入指定的字词。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # 稍微提高创造性
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            word_count = len(content)
            
            # 验证必须用到的字是否都包含在内容中
            required_words = chapter_info.get('required_words', [])
            used_words = []
            still_missing_words = []
            
            if required_words:
                for word in required_words:
                    if word in content:
                        used_words.append(word)
                    else:
                        still_missing_words.append(word)
            
            return {
                "content": content,
                "word_count": word_count,
                "status": "completed",
                "required_words": required_words,
                "used_words": used_words,
                "missing_words": still_missing_words,
                "words_completion_rate": len(used_words) / len(required_words) if required_words else 1.0,
                "is_regenerated": True
            }
                
        except Exception as e:
            print(f"重新生成章节时出错: {e}")
            return {
                "content": f"第{chapter_info['number']}章重新生成失败，请重试。",
                "word_count": 0,
                "status": "failed",
                "is_regenerated": True
            }
