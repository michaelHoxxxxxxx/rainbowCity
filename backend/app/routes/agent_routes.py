"""
彩虹城AI-Agent对话管理系统API路由
"""

from flask import Blueprint, request, jsonify, current_app
import json
import os
import uuid
import base64
from datetime import datetime
from app.agent.ai_assistant import AIAssistant
from app.agent.image_processor import ImageData, handle_file_upload

# 创建API蓝图
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# 创建AI助手实例
assistant = AIAssistant(model_name="gpt-3.5-turbo")

@agent_bp.route('/chat', methods=['POST'])
def chat_agent():
    """AI-Agent聊天接口"""
    try:
        data = request.json
        
        # 获取请求数据
        user_message = data.get('user_input', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_id = data.get('user_id', 'anonymous')
        ai_id = data.get('ai_id', 'ai_rainbow_city')
        image_data = data.get('image_data')  # 获取图片数据（如果有）
        
        # 创建AI助手实例
        ai_assistant = AIAssistant()
        
        # 处理用户查询
        result = ai_assistant.process_query(
            user_input=user_message,
            session_id=session_id,
            user_id=user_id,
            ai_id=ai_id,
            image_data=image_data
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/chat/with_image', methods=['POST'])
def chat_with_image():
    """带图片的AI-Agent聊天接口"""
    try:
        # 检查是否有文件部分
        if 'image' not in request.files and 'user_input' not in request.form:
            return jsonify({'error': '请求缺少必要参数'}), 400
        
        # 获取用户文本输入
        user_message = request.form.get('user_input', '')
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        user_id = request.form.get('user_id', 'anonymous')
        ai_id = request.form.get('ai_id', 'ai_rainbow_city')
        
        # 处理图片
        image_file = request.files.get('image')
        image_data = None
        
        if image_file and image_file.filename:
            try:
                # 读取图片内容
                image_content = image_file.read()
                # Base64编码
                image_base64 = base64.b64encode(image_content).decode('utf-8')
                # 添加数据URL前缀
                mime_type = image_file.content_type or 'image/jpeg'
                image_data = f"data:{mime_type};base64,{image_base64}"
            except Exception as e:
                return jsonify({'error': f'图片处理失败: {str(e)}'}), 400
        
        # 创建AI助手实例
        ai_assistant = AIAssistant()
        
        # 处理用户查询
        result = ai_assistant.process_query(
            user_input=user_message,
            session_id=session_id,
            user_id=user_id,
            ai_id=ai_id,
            image_data=image_data
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取会话历史"""
    try:
        history = assistant.get_conversation_history(session_id)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "history": history
        })
        
    except Exception as e:
        current_app.logger.error(f"获取会话历史时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/logs/<session_id>', methods=['GET'])
def get_logs(session_id):
    """获取会话日志"""
    try:
        logs = assistant.get_session_logs(session_id)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "logs": logs
        })
        
    except Exception as e:
        current_app.logger.error(f"获取会话日志时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_bp.route('/session/clear/<session_id>', methods=['POST'])
def clear_session(session_id):
    """清除会话数据"""
    try:
        success = assistant.clear_session(session_id)
        
        return jsonify({
            "success": success,
            "session_id": session_id,
            "message": "会话数据已清除" if success else "未找到指定会话"
        })
        
    except Exception as e:
        current_app.logger.error(f"清除会话数据时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
