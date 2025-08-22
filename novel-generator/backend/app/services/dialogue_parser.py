import re
from typing import List, Dict, Any, Optional
from ..models.dialogue import DialogueSegment, SpeakerType


class DialogueParser:
    """对话解析器 - 智能识别主角对白和其他角色对白"""
    
    def __init__(self):
        self.protagonist_patterns = [
            r'"([^"]*)"[，,。]?\s*([我我们][说道曰言]|主角说|亚瑟说)',  # "xxx",我说
            r'([我我们])[说道曰言][：:]?"([^"]*)"',  # 我说："xxx"
            r'主角[说道曰言][：:]?"([^"]*)"',  # 主角说："xxx"
            r'"([^"]*)"[，,。]?\s*[我我们]',  # "xxx",我
            r'([我我们])([想心]道|暗想|心中|内心)[：:]?"?([^"]*)"?',  # 我想道："xxx"
        ]
        
        self.character_dialogue_patterns = [
            r'(\w+)[说道曰言][：:]?"([^"]*)"',  # 张三说："xxx"
            r'"([^"]*)"[，,。]?\s*(\w+)说',  # "xxx",张三说
            r'(\w+)[问答回复][：:]?"([^"]*)"',  # 张三问："xxx"
        ]
        
        self.narrator_patterns = [
            r'^[^"]*[。！？]$',  # 没有引号的叙述句
            r'^\s*[第]\w+[章节][：:]',  # 章节标题
        ]
    
    def parse_novel_content(self, content: str) -> List[DialogueSegment]:
        """解析小说内容为对话片段"""
        segments = []
        
        # 按段落分割
        paragraphs = self._split_paragraphs(content)
        sequence = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 解析段落中的对话
            paragraph_segments = self._parse_paragraph(paragraph, sequence)
            segments.extend(paragraph_segments)
            sequence += len(paragraph_segments)
        
        return segments
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """分割段落"""
        # 按换行符分割，保留章节结构
        paragraphs = content.split('\n')
        
        # 合并相关段落（如对话和动作描述）
        merged_paragraphs = []
        current_paragraph = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                if current_paragraph:
                    merged_paragraphs.append(current_paragraph)
                    current_paragraph = ""
                continue
            
            # 章节标题单独处理
            if re.match(r'^[第]\w+[章节][：:]', para):
                if current_paragraph:
                    merged_paragraphs.append(current_paragraph)
                merged_paragraphs.append(para)
                current_paragraph = ""
            else:
                current_paragraph += " " + para if current_paragraph else para
        
        if current_paragraph:
            merged_paragraphs.append(current_paragraph)
        
        return merged_paragraphs
    
    def _parse_paragraph(self, paragraph: str, start_sequence: int) -> List[DialogueSegment]:
        """解析单个段落"""
        segments = []
        sequence = start_sequence
        
        # 检查是否是章节标题
        if re.match(r'^[第]\w+[章节][：:]', paragraph):
            segments.append(DialogueSegment(
                speaker_type=SpeakerType.NARRATOR,
                speaker_name="旁白",
                content=paragraph,
                sequence=sequence
            ))
            return segments
        
        # 查找所有引号对话
        dialogue_matches = list(re.finditer(r'"([^"]*)"', paragraph))
        
        if not dialogue_matches:
            # 没有对话，整段作为旁白
            segments.append(DialogueSegment(
                speaker_type=SpeakerType.NARRATOR,
                speaker_name="旁白",
                content=paragraph,
                sequence=sequence
            ))
            return segments
        
        # 有对话的情况
        last_end = 0
        
        for match in dialogue_matches:
            start, end = match.span()
            dialogue_content = match.group(1)
            
            # 处理对话前的叙述
            if start > last_end:
                narrator_text = paragraph[last_end:start].strip()
                if narrator_text:
                    segments.append(DialogueSegment(
                        speaker_type=SpeakerType.NARRATOR,
                        speaker_name="旁白",
                        content=narrator_text,
                        sequence=sequence
                    ))
                    sequence += 1
            
            # 识别说话者
            speaker_info = self._identify_speaker(paragraph, start, end, dialogue_content)
            
            segments.append(DialogueSegment(
                speaker_type=speaker_info["type"],
                speaker_name=speaker_info["name"],
                content=dialogue_content,
                sequence=sequence
            ))
            sequence += 1
            last_end = end
        
        # 处理最后的叙述
        if last_end < len(paragraph):
            narrator_text = paragraph[last_end:].strip()
            if narrator_text:
                segments.append(DialogueSegment(
                    speaker_type=SpeakerType.NARRATOR,
                    speaker_name="旁白",
                    content=narrator_text,
                    sequence=sequence
                ))
        
        return segments
    
    def _identify_speaker(self, paragraph: str, dialogue_start: int, dialogue_end: int, 
                         dialogue_content: str) -> Dict[str, Any]:
        """识别说话者"""
        
        # 获取对话前后的上下文
        before_text = paragraph[:dialogue_start]
        after_text = paragraph[dialogue_end:]
        
        # 检查是否是主角对话
        if self._is_protagonist_dialogue(before_text, after_text, dialogue_content):
            return {
                "type": SpeakerType.PROTAGONIST,
                "name": "主角"
            }
        
        # 检查是否是其他角色对话
        character_name = self._extract_character_name(before_text, after_text)
        if character_name:
            return {
                "type": SpeakerType.CHARACTER,
                "name": character_name
            }
        
        # 默认归类为其他角色
        return {
            "type": SpeakerType.CHARACTER,
            "name": "未知角色"
        }
    
    def _is_protagonist_dialogue(self, before_text: str, after_text: str, content: str) -> bool:
        """判断是否是主角对话"""
        
        # 检查前文
        protagonist_indicators = [
            r'[我我们][说道曰言想]',
            r'主角[说道曰言]',
            r'亚瑟[说道曰言]',  # 基于示例小说的主角名
            r'[我我们](?:心中|内心|暗想)'
        ]
        
        for pattern in protagonist_indicators:
            if re.search(pattern, before_text[-20:]):  # 检查前20个字符
                return True
        
        # 检查后文
        if re.search(r'[我我们][说道曰言]', after_text[:20]):
            return True
        
        # 检查内容特征（第一人称思考、内心独白等）
        first_person_patterns = [
            r'^[我我们]',
            r'[我我们](?:想|觉得|认为|感到)',
            r'(?:看来|原来|难道)'
        ]
        
        for pattern in first_person_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _extract_character_name(self, before_text: str, after_text: str) -> Optional[str]:
        """提取角色名字"""
        
        # 从前文提取
        before_match = re.search(r'(\w+)[说道曰言问答回复]', before_text[-20:])
        if before_match:
            name = before_match.group(1)
            if name not in ['我', '我们', '主角']:
                return name
        
        # 从后文提取
        after_match = re.search(r'(\w+)[说道曰言]', after_text[:20])
        if after_match:
            name = after_match.group(1)
            if name not in ['我', '我们', '主角']:
                return name
        
        return None
    
    def analyze_required_characters(self, dialogue_segments: List[DialogueSegment], 
                                  required_chars: List[str]) -> Dict[str, Any]:
        """分析必须字符在主角对话中的使用情况"""
        
        protagonist_dialogues = [
            segment for segment in dialogue_segments 
            if segment.speaker_type == SpeakerType.PROTAGONIST
        ]
        
        used_chars = set()
        dialogue_char_usage = []
        
        for dialogue in protagonist_dialogues:
            chars_in_dialogue = []
            for char in required_chars:
                if char in dialogue.content:
                    chars_in_dialogue.append(char)
                    used_chars.add(char)
            
            dialogue.required_chars_used = chars_in_dialogue
            dialogue_char_usage.append({
                "dialogue": dialogue.content,
                "chars_used": chars_in_dialogue
            })
        
        return {
            "total_required_chars": len(required_chars),
            "used_chars_count": len(used_chars),
            "used_chars": list(used_chars),
            "unused_chars": [char for char in required_chars if char not in used_chars],
            "usage_rate": len(used_chars) / len(required_chars) if required_chars else 0,
            "dialogue_char_usage": dialogue_char_usage
        }
