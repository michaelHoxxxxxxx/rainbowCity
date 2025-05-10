from flask import Blueprint, request, Response, current_app
import json
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取OpenAI API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 初始OpenAI客户端
client = OpenAI(api_key=OPENAI_API_KEY)

# 创建API蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

# 设置CORS，允许前端访问
@chat_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 添加一个简单的非流式聊天端点，用于测试
@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # 添加系统消息，定义AI助手的角色和行为
        system_message = {
            "role": "system",
            "content": "你是彩虹城一体七翼系统的AI助手，专门解答关于一体七翼系统、频率编号和关系管理的问题。你还需要了解关于频率编号生成器的信息，包括它如何生成频率编号，以及如何在没有pybase62库的情况下使用base64编码作为替代方案。"
        }
        
        # 准备发送给OpenAI的消息
        openai_messages = [system_message]
        for msg in messages:
            if msg.get('role') in ['user', 'assistant']:
                openai_messages.append({
                    "role": msg.get('role'),
                    "content": msg.get('content', '')
                })
        
        # 输出调试信息
        print(f"Processing messages: {json.dumps(messages)}")
        
        # 使用OpenAI客户端的API（非流式）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages
        )
        
        # 提取回复内容
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            
            # 构造AI SDK兼容的响应格式
            response_data = {
                "id": str(response.id),
                "object": "chat.completion",
                "created": int(response.created),
                "model": response.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ]
            }
            
            print(f"Sending response: {content[:50]}...")
            
            # 返回JSON响应
            return response_data
        else:
            error_message = "OpenAI API 响应中没有内容"
            print(error_message)
            return {"error": error_message}, 500
            
    except Exception as e:
        print(f"Chat error: {str(e)}")
        
        return {"error": str(e)}, 500

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
