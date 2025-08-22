import re
from typing import Dict, List, Any, Optional
from ..models.material import RequiredCharacter, WritingGuideline


class MaterialParser:
    """材料文件解析器"""
    
    def parse_material_file(self, content: str, filename: str) -> Dict[str, Any]:
        """解析材料文件内容"""
        
        # 基础信息
        title = self._extract_title(content, filename)
        category = self._extract_category(content)
        example_novels = self._extract_example_novels(content)
        writing_guidelines = self._extract_writing_guidelines(content)
        required_characters = self._extract_required_characters(content)
        pinyin_character_count = self._extract_pinyin_count(content)
        
        return {
            "title": title,
            "category": category,
            "example_novels": example_novels,
            "writing_guidelines": writing_guidelines,
            "required_characters": required_characters,
            "pinyin_character_count": pinyin_character_count,
            "file_name": filename,
            "file_content": content
        }
    
    def _extract_title(self, content: str, filename: str) -> str:
        """提取标题"""
        # 尝试从第一个一级标题提取
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # 如果没有找到，使用文件名
        return filename.replace('.md', '').replace('.markdown', '').replace('.txt', '')
    
    def _extract_category(self, content: str) -> str:
        """提取小说类别"""
        # 查找包含"类"的行
        category_match = re.search(r'第\d+类[：:]\s*(.+)', content)
        if category_match:
            return category_match.group(0).strip()
        
        # 查找标题中的类别信息
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        return "未分类"
    
    def _extract_example_novels(self, content: str) -> List[str]:
        """提取示例小说"""
        novels = []
        
        # 查找示例小说行
        example_match = re.search(r'\*\*示例小说\*\*[：:]?\s*(.+)', content)
        if example_match:
            novels_text = example_match.group(1).strip()
            # 分割小说名称（支持逗号、顿号、空格分隔）
            novels = re.split(r'[，,、\s]+', novels_text)
            novels = [novel.strip() for novel in novels if novel.strip()]
        
        return novels
    
    def _extract_writing_guidelines(self, content: str) -> WritingGuideline:
        """提取写作指导"""
        guidelines = {
            "world_building": "",
            "character_development": "",
            "background_setting": "",
            "plot_development": "",
            "language_style": ""
        }
        
        # 查找写作指导部分
        guideline_section = re.search(r'\*\*写作指导\*\*[：:]?\s*\n(.*?)(?=\n\*\*|\n##|\Z)', 
                                    content, re.DOTALL)
        
        if guideline_section:
            guideline_text = guideline_section.group(1)
            
            # 提取各个指导项
            patterns = {
                "world_building": r'[*-]\s*\*\*世界观设定\*\*[：:]?\s*(.+)',
                "character_development": r'[*-]\s*\*\*角色刻画\*\*[：:]?\s*(.+)',
                "background_setting": r'[*-]\s*\*\*背景设定\*\*[：:]?\s*(.+)',
                "plot_development": r'[*-]\s*\*\*情节发展\*\*[：:]?\s*(.+)',
                "language_style": r'[*-]\s*\*\*语言风格\*\*[：:]?\s*(.+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, guideline_text)
                if match:
                    guidelines[key] = match.group(1).strip()
        
        return WritingGuideline(**guidelines)
    
    def _extract_required_characters(self, content: str) -> List[RequiredCharacter]:
        """提取必须使用的汉字"""
        characters = []
        
        # 查找汉字表格或列表
        # 模式1: 数字. 拼音 → 汉字
        pattern1 = re.findall(r'\d+\.\s+(\w+)\s+→\s+(\S)', content)
        for pinyin, char in pattern1:
            characters.append(RequiredCharacter(pinyin=pinyin, character=char))
        
        # 模式2: 拼音: 汉字
        pattern2 = re.findall(r'(\w+)[：:]\s*(\S)', content)
        for pinyin, char in pattern2:
            if len(char) == 1 and '\u4e00' <= char <= '\u9fff':  # 确保是中文字符
                characters.append(RequiredCharacter(pinyin=pinyin, character=char))
        
        return characters
    
    def _extract_pinyin_count(self, content: str) -> int:
        """提取拼音汉字对数"""
        # 查找拼音汉字对数
        count_match = re.search(r'\*\*拼音汉字对数\*\*[：:]?\s*(\d+)', content)
        if count_match:
            return int(count_match.group(1))
        
        # 如果没有找到，计算required_characters的数量
        characters = self._extract_required_characters(content)
        return len(characters)
    
    def validate_material(self, material) -> Dict[str, Any]:
        """验证材料完整性"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 必填字段检查
        if not material.title:
            validation_result["errors"].append("缺少标题")
        
        if not material.category:
            validation_result["errors"].append("缺少类别信息")
        
        # 写作指导完整性检查
        guidelines = material.writing_guidelines
        if not any([guidelines.world_building, guidelines.character_development, 
                   guidelines.background_setting, guidelines.plot_development, 
                   guidelines.language_style]):
            validation_result["warnings"].append("写作指导信息不完整")
        
        # 必须字符检查
        if not material.required_characters:
            validation_result["warnings"].append("未找到必须使用的汉字")
        elif len(material.required_characters) != material.pinyin_character_count:
            validation_result["warnings"].append(
                f"拼音汉字对数({material.pinyin_character_count})与实际字符数量({len(material.required_characters)})不匹配"
            )
        
        # 示例小说检查
        if not material.example_novels:
            validation_result["warnings"].append("未找到示例小说")
        
        validation_result["is_valid"] = len(validation_result["errors"]) == 0
        
        return validation_result