"""
上下文构建器
负责构建和管理对话上下文，包括消息历史和工具调用结果
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import base64
from datetime import datetime
from .image_processor import ImageData, ImageProcessor
import time

@dataclass
class ContextBuilder:
    """上下文构建和管理"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    session_id: str = ""
    user_id: str = ""
    ai_id: str = ""
    
    def build_initial_context(self, user_input: str) -> List[Dict[str, Any]]:
        """构建初始上下文"""
        system_message = {
            "role": "system",
            "content": "你是彩虹城系统的AI助手，专门解答关于彩虹城系统、一体七翼、频率编号和关系管理的问题。如果需要外部数据，请明确说明需要调用什么工具。"
        }
        user_message = {
            "role": "user", 
            "content": user_input
        }
        
        self.messages = [system_message, user_message]
        return self.messages
    
    def update_context_with_tool_result(self, tool_name: str, tool_result: str, tool_call_id: str = None) -> List[Dict[str, Any]]:
        """将工具结果插入上下文
        
        注意：OpenAI API要求'tool'角色的消息必须是对之前包含'tool_calls'的消息的响应
        因此，我们需要先添加一个助手消息，其中包含工具调用信息
        """
        # 查找最后一条助手消息，看是否已经包含工具调用
        has_assistant_with_tool_calls = False
        for msg in reversed(self.messages):
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                has_assistant_with_tool_calls = True
                break
        
        # 如果没有包含工具调用的助手消息，添加一个
        if not has_assistant_with_tool_calls:
            # 生成一个工具调用ID
            call_id = tool_call_id or f"call_{int(time.time())}"
            
            # 添加一个助手消息，包含工具调用信息
            assistant_message = {
                "role": "assistant",
                "content": None,  # 使用工具时，内容可以为空
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": "{}"
                        }
                    }
                ]
            }
            self.messages.append(assistant_message)
        
        # 现在添加工具响应消息
        tool_message = {
            "role": "tool",
            "tool_call_id": tool_call_id or f"call_{int(time.time())}",
            "name": tool_name,
            "content": tool_result
        }
        
        self.messages.append(tool_message)
        self.tool_results.append({
            "tool_name": tool_name,
            "result": tool_result,
            "timestamp": datetime.now().isoformat()
        })
        
        return self.messages
    
    def add_assistant_message(self, content: str) -> List[Dict[str, Any]]:
        """添加助手消息到上下文"""
        assistant_message = {
            "role": "assistant",
            "content": content
        }
        
        self.messages.append(assistant_message)
        return self.messages
    
    def update_context_with_user_message(self, user_input: str, image_data: Optional[str] = None) -> List[Dict[str, Any]]:
        """使用用户输入更新上下文，支持文本和图片"""
        # 如果有图片数据，创建多模态消息
        if image_data:
            user_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    self._format_image_data(image_data)
                ]
            }
        else:
            # 纯文本消息
            user_message = {
                "role": "user",
                "content": user_input
            }
            
        self.messages.append(user_message)
        return self.messages
        
    def _format_image_data(self, image_data: str) -> Dict[str, Any]:
        """格式化图片数据为OpenAI兼容格式"""
        # 如果是URL
        if image_data.startswith(('http://', 'https://', 'data:image')):
            return {
                "type": "image_url",
                "image_url": {"url": image_data}
            }
        
        # 如果是Base64编码
        try:
            # 尝试解码来验证是否为有效的Base64
            base64.b64decode(image_data)
            # 添加数据 URL前缀，如果还没有
            if not image_data.startswith('data:image'):
                image_data = f"data:image/jpeg;base64,{image_data}"
                
            return {
                "type": "image_url",
                "image_url": {"url": image_data}
            }
        except Exception:
            # 如果不是有效的Base64，则将其作为文本处理
            return {"type": "text", "text": f"[Image data could not be processed: {image_data[:30]}...]"}
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.messages
    
    def clear_context(self) -> None:
        """清除上下文"""
        self.messages = []
        self.tool_results = []
