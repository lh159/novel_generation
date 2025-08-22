from typing import Dict, Any, Optional, List
import json
import random
from ..config import settings
from .deepseek_client import DeepSeekClient
from ..models.material import Material
from .dialogue_parser import DialogueParser


class NovelGenerator:
    """增强的小说生成器 - 支持材料投喂和对话系统"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.deepseek_api_key
        self.dialogue_parser = DialogueParser()
        try:
            if self.api_key:
                self.client = DeepSeekClient(self.api_key)
            else:
                self.client = None
        except Exception as e:
            print(f"DeepSeek客户端初始化失败: {e}")
            self.client = None
    
    async def generate_novel_content(self, 
                                   title: str,
                                   description: str,
                                   genre: str,
                                   style: str,
                                   character_info: str,
                                   plot_outline: str,
                                   material_id: Optional[str] = None) -> str:
        """生成完整的小说内容（支持材料投喂）"""
        
        # 获取材料信息
        material = None
        if material_id:
            try:
                material = await Material.get(material_id)
                print(f"📚 使用材料: {material.title if material else '未找到'}")
            except Exception as e:
                print(f"⚠️ 材料获取失败: {e}")
        
        if not self.client:
            return self._generate_mock_content(title, description, genre, material)
        
        prompt = self._build_enhanced_novel_prompt(
            title, description, genre, style, character_info, plot_outline, material
        )
        
        try:
            print(f"🤖 开始生成小说内容: {title}")
            content = await self.client.generate_novel_content(prompt)
            print(f"✅ 小说内容生成完成，长度: {len(content)} 字符")
            
            # 分析对话和必须字符使用情况
            if material and material.required_characters:
                self._analyze_character_usage(content, material)
            
            return content
        except Exception as e:
            print(f"❌ AI生成失败: {e}")
            return self._generate_mock_content(title, description, genre, material)
    
    def _build_enhanced_novel_prompt(self, title: str, description: str, genre: str, 
                                   style: str, character_info: str, plot_outline: str, 
                                   material: Optional[Material] = None) -> str:
        """构建增强的小说生成提示词（基于材料投喂）"""
        
        # 基础提示词
        prompt = f"""
        请根据以下要求创作一部完整的小说：
        
        标题：{title}
        描述：{description}
        类型：{genre}
        风格：{style}
        人物设定：{character_info}
        情节大纲：{plot_outline}
        """
        
        # 如果有材料，添加材料指导
        if material:
            prompt += f"""
        
        【重要：材料投喂指导】
        小说类别：{material.category}
        """
            
            if material.example_novels:
                prompt += f"参考小说：{', '.join(material.example_novels)}\n"
            
            # 添加写作指导
            guidelines = material.writing_guidelines
            if guidelines:
                prompt += "\n写作指导要求：\n"
                if guidelines.world_building:
                    prompt += f"• 世界观设定：{guidelines.world_building}\n"
                if guidelines.character_development:
                    prompt += f"• 角色刻画：{guidelines.character_development}\n"
                if guidelines.background_setting:
                    prompt += f"• 背景设定：{guidelines.background_setting}\n"
                if guidelines.plot_development:
                    prompt += f"• 情节发展：{guidelines.plot_development}\n"
                if guidelines.language_style:
                    prompt += f"• 语言风格：{guidelines.language_style}\n"
            
            # 添加必须使用的汉字要求
            if material.required_characters:
                required_chars = [char.character for char in material.required_characters]
                prompt += f"""
        
        【核心要求：必须使用指定汉字】
        在主角的对话中，必须自然地使用以下汉字：
        {', '.join(required_chars)}
        
        注意：
        1. 这些汉字必须出现在主角的对话（引号内的内容）中
        2. 使用要自然流畅，不能生硬插入
        3. 主角对话要丰富，确保有足够机会使用这些字符
        4. 其他角色对话无此限制
        """
        
        # 通用要求
        prompt += """
        
        【创作要求】
        1. 生成完整的小说内容，包含5-8个章节
        2. 每个章节1000-1500字，总长度5000-8000字
        3. 包含大量对话，特别是主角对话
        4. 人物性格鲜明，对话符合角色特点
        5. 情节连贯，符合所选类型和风格
        6. 主角对话要丰富多样，便于沉浸式阅读
        
        【格式要求】
        请按以下结构返回小说内容：
        
        第一章：[章节标题]
        [章节内容，包含对话和叙述...]
        
        第二章：[章节标题]
        [章节内容，包含对话和叙述...]
        
        以此类推...
        
        【对话要求】
        
        1. 主角对话要符合人物设定
        2. 对话要推动剧情发展
        3. 确保主角有充足的对话机会
        
        **【重要格式要求】**：
        5. 对话部分必须按以下格式标记：
           - 旁白和叙述部分：在段落开头标注"正文："
           - 主角说话：标注"主角："后跟对话内容
           - 其他角色说话：标注"角色名："或"其他角色："后跟对话内容
           
        示例格式：
        正文：雨水混杂着霓虹灯光，在潮湿的巷道上折射出迷离的光晕。
        主角：你迟到了，这次的任务很重要。
        其他角色：抱歉，路上遇到了一些麻烦。
        正文：他看向远处的大楼，心中涌起不安的预感。
        
        请直接返回小说正文，不要添加任何解释或格式说明。
        """
        
        return prompt
    
    def _generate_mock_content(self, title: str, description: str, genre: str, 
                             material: Optional[Material] = None) -> str:
        """生成模拟小说内容（当AI不可用时）"""
        
        # 如果有材料，尝试使用必须字符
        required_chars = []
        if material and material.required_characters:
            required_chars = [char.character for char in material.required_characters[:10]]  # 使用前10个
        
        # 构建包含必须字符的主角对话
        protagonist_dialogues = [
            "\"今天似乎有些不同。\"我望着窗外，心中涌起一种莫名的预感。",
            "\"这一切都不是巧合。\"我喃喃自语，眼中闪烁着坚定的光芒。",
            "\"原来如此，所有的线索都指向同一个方向。\"我恍然大悟。",
            "\"现在后悔还来得及吗？\"我苦笑道，但眼中的决心却更加坚定。",
            "\"无论结果如何，我都不会后悔。\"我深吸一口气，迎向了自己的命运。"
        ]
        
        # 如果有必须字符，随机插入到对话中
        if required_chars:
            for i, char in enumerate(required_chars[:len(protagonist_dialogues)]):
                old_dialogue = protagonist_dialogues[i]
                # 简单地在对话中插入字符（实际应用中需要更智能的插入方式）
                new_dialogue = old_dialogue.replace("我", f"我{char}然")
                protagonist_dialogues[i] = new_dialogue
        
        mock_content = f"""第一章：序幕

{description}

这是一个关于{genre}的故事。主角在一个平凡的日子里，突然发现自己的生活即将发生巨大的变化。

{protagonist_dialogues[0]}

第二章：初现端倪

随着时间的推移，奇异的事件开始接连发生。主角意识到，自己可能卷入了一个远超想象的事件中。

{protagonist_dialogues[1]}

第三章：真相渐显

经过一番调查，主角终于发现了事件背后的真相。原来一切都与一个古老的秘密有关。

{protagonist_dialogues[2]}

第四章：危机四伏

知晓真相的主角并没有感到轻松，反而意识到自己正面临着前所未有的危险。

{protagonist_dialogues[3]}

第五章：最终对决

在经历了重重考验后，主角终于迎来了最终的挑战。这是决定一切的关键时刻。

{protagonist_dialogues[4]}

尾声：新的开始

当一切尘埃落定，主角回望来路，发现自己已经成长了许多。虽然经历了种种困难，但这段经历也让他收获了宝贵的财富。

这就是{title}的故事，一个关于成长、勇气和坚持的传奇。

[注：由于AI服务暂时不可用，以上为示例内容。请配置DeepSeek API密钥以获得完整的AI生成内容。]"""
        
        if material:
            mock_content += f"\n\n[使用材料：{material.title}]"
            if required_chars:
                mock_content += f"\n[已尝试使用必须字符：{', '.join(required_chars)}]"
        
        return mock_content.strip()
    
    def _analyze_character_usage(self, content: str, material: Material) -> Dict[str, Any]:
        """分析小说中必须字符的使用情况"""
        
        # 解析对话
        dialogue_segments = self.dialogue_parser.parse_novel_content(content)
        
        # 分析必须字符使用
        required_chars = [char.character for char in material.required_characters]
        analysis = self.dialogue_parser.analyze_required_characters(dialogue_segments, required_chars)
        
        print(f"📊 字符使用分析:")
        print(f"   总必须字符: {analysis['total_required_chars']}")
        print(f"   已使用字符: {analysis['used_chars_count']}")
        print(f"   使用率: {analysis['usage_rate']:.1%}")
        
        if analysis['unused_chars']:
            print(f"   未使用字符: {', '.join(analysis['unused_chars'])}")
        
        return analysis
    
    async def generate_with_material_validation(self, 
                                              title: str,
                                              description: str, 
                                              genre: str,
                                              style: str,
                                              character_info: str,
                                              plot_outline: str,
                                              material_id: str,
                                              max_retries: int = 3) -> Dict[str, Any]:
        """带材料验证的小说生成（如果字符使用率不达标会重试）"""
        
        material = await Material.get(material_id)
        if not material:
            raise ValueError("材料不存在")
        
        required_chars = [char.character for char in material.required_characters]
        min_usage_rate = 0.8  # 最低使用率要求
        
        for attempt in range(max_retries):
            print(f"🎯 第 {attempt + 1} 次生成尝试")
            
            content = await self.generate_novel_content(
                title, description, genre, style, character_info, plot_outline, material_id
            )
            
            # 分析字符使用情况
            dialogue_segments = self.dialogue_parser.parse_novel_content(content)
            analysis = self.dialogue_parser.analyze_required_characters(dialogue_segments, required_chars)
            
            if analysis['usage_rate'] >= min_usage_rate:
                print(f"✅ 字符使用率达标: {analysis['usage_rate']:.1%}")
                return {
                    "content": content,
                    "analysis": analysis,
                    "attempt": attempt + 1,
                    "success": True
                }
            else:
                print(f"⚠️ 字符使用率不达标: {analysis['usage_rate']:.1%}，需要重试")
        
        print(f"❌ 经过 {max_retries} 次尝试，仍未达到字符使用率要求")
        return {
            "content": content,
            "analysis": analysis,
            "attempt": max_retries,
            "success": False
        }
