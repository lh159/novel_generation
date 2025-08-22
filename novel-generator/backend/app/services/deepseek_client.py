import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional
from ..config import settings

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.deepseek_api_key
        self.api_base = settings.deepseek_api_base
        self.model = settings.deepseek_model
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.8,
        stream: bool = False
    ) -> Dict[str, Any]:
        """调用DeepSeek聊天完成API"""
        
        url = f"{self.api_base}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            # 为长文本生成增加超时时间
            timeout = httpx.Timeout(300.0, connect=30.0, read=300.0, write=30.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                print(f"🌐 发送请求到: {url}")
                print(f"🔑 使用API密钥: {self.api_key[:8]}...")
                print(f"📊 请求载荷大小: {len(json.dumps(payload))} 字符")
                
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload
                )
                
                print(f"📡 收到响应状态: {response.status_code}")
                print(f"📄 响应内容长度: {len(response.text)} 字符")
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # 检查响应内容是否为空
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        message = response_data['choices'][0]['message']
                        content = message.get('content', '')
                        reasoning_content = message.get('reasoning_content', '')
                        
                        # DeepSeek-reasoner模型优先使用reasoning_content
                        final_content = content if content and content.strip() else reasoning_content
                        
                        if not final_content or final_content.strip() == "":
                            print("⚠️ API返回空内容，可能是因为:")
                            print("   1. 请求内容触发了安全过滤")
                            print("   2. API服务器临时问题")
                            print("   3. 请求超出了模型能力范围")
                            print("🔄 建议稍后重试或调整提示词")
                        else:
                            print(f"✅ 获得有效响应，内容长度: {len(final_content)} 字符")
                            if reasoning_content and not content:
                                print("🧠 使用reasoning_content作为主要内容")
                    
                    return response_data
                else:
                    error_msg = f"API调用失败: {response.status_code} - {response.text}"
                    print(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.ReadTimeout:
            error_msg = "DeepSeek API请求超时，请稍后重试"
            print(error_msg)
            raise Exception(error_msg)
        except httpx.ConnectTimeout:
            error_msg = "连接DeepSeek API超时，请检查网络连接"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"DeepSeek API调用异常: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    async def generate_novel_content(self, prompt: str, max_retries: int = 3) -> str:
        """生成小说内容（带重试机制）"""
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的小说创作助手，擅长创作包含大量对白的小说。请严格按照用户要求创作，确保对白自然流畅，情节完整。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试 {attempt + 1}/{max_retries}")
                
                response = await self.chat_completion(
                    messages=messages,
                    max_tokens=10000,  # 增加token限制确保完整输出
                    temperature=0.8
                )
                
                if 'choices' in response and len(response['choices']) > 0:
                    message = response['choices'][0]['message']
                    content = message.get('content', '')
                    reasoning_content = message.get('reasoning_content', '')
                    
                    # DeepSeek-reasoner模型优先使用reasoning_content
                    final_content = content if content and content.strip() else reasoning_content
                    
                    # 检查内容是否为空
                    if final_content and final_content.strip():
                        print(f"✅ 第 {attempt + 1} 次尝试成功！")
                        if reasoning_content and not content:
                            print("🧠 使用reasoning_content作为主要内容")
                        return final_content
                    else:
                        print(f"⚠️ 第 {attempt + 1} 次尝试返回空内容")
                        if attempt < max_retries - 1:
                            print("🔄 等待3秒后重试...")
                            await asyncio.sleep(3)
                            continue
                        else:
                            raise Exception("多次尝试后仍返回空内容")
                else:
                    raise Exception("API响应格式错误")
                    
            except Exception as e:
                print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print("🔄 等待5秒后重试...")
                    await asyncio.sleep(5)
                    continue
                else:
                    print(f"💔 {max_retries} 次尝试全部失败")
                    raise e
