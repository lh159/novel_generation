from typing import List, Dict, Any
import uuid
from datetime import datetime

class ProtagonistRoleplaySystem:
    """主角扮演系统"""
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, novel_id: int) -> str:
        """创建用户主角扮演会话"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'novel_id': novel_id,
            'current_chapter': 1,
            'dialogue_history': [],
            'current_dialogue_index': 0,
            'waiting_for_user_confirmation': False,
            'current_protagonist_dialogue': None
        }
        return session_id
    
    def get_current_dialogue(self, session_id: str, dialogues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取当前对白状态"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")
        
        session = self.active_sessions[session_id]
        
        if session['current_dialogue_index'] >= len(dialogues):
            return {
                'speaker': '系统',
                'text': '本章节已结束，是否进入下一章节？',
                'required_chars_used': [],
                'is_end_of_chapter': True,
                'is_protagonist_dialogue': False
            }
        
        current_dialogue = dialogues[session['current_dialogue_index']]
        
        # 判断是否是主角对白
        is_protagonist = current_dialogue.get('is_protagonist', False)
        
        if is_protagonist and not session['waiting_for_user_confirmation']:
            # 主角对白，等待用户确认
            session['waiting_for_user_confirmation'] = True
            session['current_protagonist_dialogue'] = current_dialogue
            return {
                'speaker': '主角',
                'text': current_dialogue['text'],
                'required_chars_used': current_dialogue.get('required_chars_used', []),
                'is_protagonist_dialogue': True,
                'waiting_confirmation': True,
                'message': '请阅读完主角台词后点击"确认读完"继续剧情'
            }
        elif not is_protagonist:
            # 其他角色对白或旁白，不在这里推进索引
            session['waiting_for_user_confirmation'] = False
            
            # 非主角对话，返回当前对话但不推进索引
            return {
                'speaker': current_dialogue['speaker'],
                'text': current_dialogue['text'],
                'required_chars_used': current_dialogue.get('required_chars_used', []),
                'is_protagonist_dialogue': False,
                'waiting_confirmation': False,  # 非主角对话不需要等待确认
                'auto_advance': True  # 非主角对话总是自动推进
            }
        
        return {
            'speaker': '系统',
            'text': '等待用户确认主角台词',
            'required_chars_used': [],
            'is_protagonist_dialogue': False,
            'waiting_confirmation': True
        }
    
    def advance_dialogue(self, session_id: str, dialogues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """推进到下一个对话（用于非主角对话的自动推进）"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")
        
        session = self.active_sessions[session_id]
        
        # 获取当前对话并记录到历史
        if session['current_dialogue_index'] < len(dialogues):
            current_dialogue = dialogues[session['current_dialogue_index']]
            session['dialogue_history'].append({
                'speaker': current_dialogue['speaker'],
                'text': current_dialogue['text'],
                'timestamp': datetime.now().isoformat(),
                'is_protagonist_dialogue': current_dialogue.get('is_protagonist', False)
            })
        
        # 推进到下一个对白
        session['current_dialogue_index'] += 1
        session['waiting_for_user_confirmation'] = False
        
        # 获取下一个对白
        return self.get_current_dialogue(session_id, dialogues)

    def confirm_protagonist_dialogue(self, session_id: str, dialogues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """用户确认已读完主角台词"""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session ID")
        
        session = self.active_sessions[session_id]
        
        if not session['waiting_for_user_confirmation']:
            return {
                'error': '当前无需确认主角台词'
            }
        
        # 记录主角对白历史
        if session['current_protagonist_dialogue']:
            session['dialogue_history'].append({
                'speaker': '主角',
                'text': session['current_protagonist_dialogue']['text'],
                'timestamp': datetime.now().isoformat(),
                'is_protagonist_dialogue': True
            })
        
        # 推进到下一个对白
        session['current_dialogue_index'] += 1
        session['waiting_for_user_confirmation'] = False
        session['current_protagonist_dialogue'] = None
        
        # 获取下一个对白
        return self.get_current_dialogue(session_id, dialogues)
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            'novel_id': session['novel_id'],
            'current_chapter': session['current_chapter'],
            'current_dialogue_index': session['current_dialogue_index'],
            'waiting_for_confirmation': session['waiting_for_user_confirmation'],
            'dialogue_history_count': len(session['dialogue_history'])
        }
