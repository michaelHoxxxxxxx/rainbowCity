from flask import Blueprint, request, Response, current_app
import json
import os
import requests
import openai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取OpenAI API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 配置OpenAI API密钥
openai.api_key = OPENAI_API_KEY

# 创建API蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

# 设置CORS，允许前端访问
@chat_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    # 添加系统消息，定义AI助手的角色和行为
    system_message = {
        "role": "system",
        "content": "你是彩虹城一体七翼系统的AI助手，专门解答关于一体七翼系统、频率编号和关系管理的问题。"
    }
    
    # 准备发送给OpenAI的消息
    openai_messages = [system_message]
    for msg in messages:
        if msg.get('role') in ['user', 'assistant']:
            openai_messages.append({
                "role": msg.get('role'),
                "content": msg.get('content', '')
            })
    
    def generate():
        try:
            # 使用OpenAI API直接调用（与1.0.0版本兼容）
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": openai_messages,
                    "stream": True
                },
                stream=True
            )
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    # 移除前缀 "data: "
                    line_text = line.decode('utf-8')
                    print(f"Received line: {line_text}")  # 记录收到的行
                    
                    if line_text.startswith('data: '):
                        line_text = line_text[6:]
                        
                        # 如果是[DONE]标记，发送结束事件
                        if line_text == "[DONE]":
                            finish_data = {"type": "finish"}
                            print(f"Sending finish: {repr(f'data: {json.dumps(finish_data)}\n\n')}")  # 记录发送的内容
                            yield f"data: {json.dumps(finish_data)}\n\n"
                            continue
                        
                        try:
                            # 解析JSON响应
                            json_data = json.loads(line_text)
                            # 提取内容增量
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                choice = json_data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta'] and choice['delta']['content']:
                                    content = choice['delta']['content']
                                    # 构造Vercel AI SDK兼容的响应格式
                                    data = {
                                        "type": "text-delta",
                                        "textDelta": content
                                    }
                                    # 确保正确格式化，带data:前缀和双换行
                                    print(f"Sending: {repr(f'data: {json.dumps(data)}\n\n')}")  # 记录发送的内容
                                    yield f"data: {json.dumps(data)}\n\n"
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, line: {line_text}")  # 记录JSON解析错误
                            continue
            
        except Exception as e:
            # 使用print而不是current_app.logger来避免应用程序上下文错误
            print(f"Stream generation error: {str(e)}")
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

@chat_bp.route('/chat/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return Response(
        json.dumps({"status": "ok", "service": "chat-service"}),
        status=200,
        mimetype='application/json'
    )

@chat_bp.route('/chat/test', methods=['POST'])
def chat_test():
    """测试端点，返回一个固定的响应"""
    def generate():
        # 返回一个固定的测试响应
        yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': '你好！'})}\n\n"
        yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': '我是彩虹城一体七翼系统的AI助手。'})}\n\n"
        yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': '我可以帮助你了解一体七翼系统、频率编号和关系管理。'})}\n\n"
        yield f"data: {json.dumps({'type': 'finish'})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

@chat_bp.route('/chat/simple', methods=['POST'])
def chat_simple():
    """简单的聊天端点，直接返回JSON响应"""
    # 获取请求数据
    data = request.json
    messages = data.get('messages', [])
    
    # 打印收到的消息，便于调试
    print("Received messages:", messages)
    
    # 获取最后一条用户消息
    user_message = None
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_message = msg.get('content', '')
            break
    
    # 预定义的回复
    responses = {
        "你好": "你好！我是彩虹城一体七翼系统的AI助手。我可以帮助你了解一体七翼系统、频率编号和关系管理。",
        "一体七翼": "一体七翼系统是Rainbow City平台的核心功能，用于生成、管理和可视化AI标识符和频率编号。它由七个不同的维度组成，每个维度都代表了AI的不同特性。",
        "频率编号": "频率编号是一体七翼系统中的重要组成部分，它用于表示AI的频率特性。每个频率编号包含了值代码、序列号、人格代码、AI类型代码和哈希签名等多个部分。",
        "关系管理": "关系管理是一体七翼系统的重要功能，用于管理AI与人类用户之间的关系。它包括了关系创建、关系搜索、关系状态更新和关系强度评分等功能。",
    }
    
    # 根据用户消息选择回复
    response = "我不太理解你的问题。可以请你再详细说明一下吗？"
    
    if user_message:
        # 尝试匹配预定义的回复
        for key, value in responses.items():
            if key in user_message:
                response = value
                break
    
    # 返回JSON响应
    return Response(
        json.dumps({"response": response}),
        status=200,
        mimetype='application/json'
    )
