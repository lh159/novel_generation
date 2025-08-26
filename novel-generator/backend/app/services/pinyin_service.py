"""
拼音转换服务
提供汉字转拼音的功能，支持缓存和多音字处理
"""

from pypinyin import pinyin, Style
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class PinyinService:
    """拼音转换服务"""
    
    def __init__(self):
        """初始化拼音服务，包含缓存机制"""
        self.cache = {}
        logger.info("PinyinService 初始化完成")
    
    def convert_text_to_pinyin(self, text: str) -> List[Dict[str, str]]:
        """
        将文本转换为拼音标注格式
        
        Args:
            text: 输入的中文文本
            
        Returns:
            拼音标注列表，格式：[{"char": "你", "pinyin": "nǐ", "is_chinese": True}, ...]
        """
        if not text:
            return []
            
        # 检查缓存
        if text in self.cache:
            logger.debug(f"从缓存获取拼音结果: {text[:10]}...")
            return self.cache[text]
        
        result = []
        
        try:
            # 使用pypinyin转换，保留声调，不显示多音字选项
            pinyin_list = pinyin(text, style=Style.TONE, heteronym=False)
            
            for i, char in enumerate(text):
                if self._is_chinese_char(char):
                    # 中文字符，添加拼音
                    py = pinyin_list[i][0] if i < len(pinyin_list) else ''
                    result.append({
                        "char": char,
                        "pinyin": py,
                        "is_chinese": True
                    })
                else:
                    # 非中文字符（标点、英文、数字等），不需要拼音
                    result.append({
                        "char": char,
                        "pinyin": "",
                        "is_chinese": False
                    })
            
            # 缓存结果（限制缓存大小避免内存泄漏）
            if len(self.cache) < 1000:  # 最多缓存1000个结果
                self.cache[text] = result
            
            logger.debug(f"成功转换文本为拼音: {text[:10]}... -> {len(result)}个字符")
            return result
            
        except Exception as e:
            logger.error(f"拼音转换失败: {text[:10]}... - {str(e)}")
            # 返回原文本，不带拼音
            return [{"char": char, "pinyin": "", "is_chinese": self._is_chinese_char(char)} 
                   for char in text]
    
    def _is_chinese_char(self, char: str) -> bool:
        """
        判断是否为中文字符
        
        Args:
            char: 单个字符
            
        Returns:
            是否为中文字符
        """
        return '\u4e00' <= char <= '\u9fff'
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("拼音服务缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def convert_simple_text(self, text: str) -> str:
        """
        简单的文本转拼音，只返回拼音字符串（用于某些特殊场景）
        
        Args:
            text: 输入文本
            
        Returns:
            拼音字符串，用空格分隔
        """
        try:
            pinyin_list = pinyin(text, style=Style.TONE, heteronym=False)
            return ' '.join([py[0] for py in pinyin_list])
        except Exception as e:
            logger.error(f"简单拼音转换失败: {text[:10]}... - {str(e)}")
            return text


# 创建全局实例
pinyin_service = PinyinService()
