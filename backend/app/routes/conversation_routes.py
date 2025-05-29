from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app.db import create, query, update
from datetime import datetime
import jwt

conversation_bp = Blueprint('conversation', __name__, url_prefix='/api/conversations')

# JWT 认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # 解码token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            
            # 查询用户
            users = query('users', {'id': user_id})
            if not users or len(users) == 0:
                return jsonify({'error': 'Invalid token'}), 401
                
            current_user = users[0]
            return f(current_user, *args, **kwargs)
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated

# 获取用户的所有对话
@conversation_bp.route('', methods=['GET'])
@token_required
def get_conversations(current_user):
    user_id = current_user.get('id')
    
    try:
        # 查询用户的所有对话 - 使用原始SQL查询
        from app.db import run_async, get_db
        
        async def _get_conversations():
            db = await get_db()
            if db is None:
                return []
            
            query_str = f"SELECT * FROM conversations WHERE user_id = '{user_id}'"
            print(f"Direct SQL query: {query_str}")
            result = await db.query(query_str)
            
            if result and result[0] and 'result' in result[0]:
                return result[0]['result']
            return []
        
        conversations = run_async(_get_conversations())
        
        # 打印详细的查询结果信息以便调试
        print(f"Raw query result for user {user_id}: {conversations}")
        
        # 如果没有找到对话，尝试使用另一种查询方式
        if not conversations:
            print("No conversations found with first method, trying alternative query...")
            
            async def _get_conversations_alt():
                db = await get_db()
                if db is None:
                    return []
                
                # 使用更直接的查询方式
                result = await db.query(f"SELECT VALUE FROM conversations WHERE user_id = '{user_id}'")
                print(f"Alternative query result: {result}")
                
                if result and isinstance(result, list) and len(result) > 0:
                    return result
                return []
            
            alt_conversations = run_async(_get_conversations_alt())
            if alt_conversations:
                conversations = alt_conversations
                print(f"Found {len(conversations)} conversations with alternative method")
        
        # 按最后更新时间排序
        if conversations:
            conversations.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        
        print(f"Returning {len(conversations)} conversations for user {user_id}")
        
        return jsonify({
            'conversations': conversations
        }), 200
    except Exception as e:
        print(f"Error fetching conversations: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500

# 创建新对话
@conversation_bp.route('', methods=['POST'])
@token_required
def create_conversation(current_user):
    user_id = current_user.get('id')
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title', '新对话')
    messages = data.get('messages', [])
    
    # 生成预览文本
    preview = ''
    if messages and len(messages) > 0:
        for msg in messages:
            if msg.get('role') == 'assistant' and msg.get('content'):
                preview = msg.get('content')[:50] + '...' if len(msg.get('content')) > 50 else msg.get('content')
                break
        
        if not preview and messages[0].get('content'):
            preview = messages[0].get('content')[:50] + '...' if len(messages[0].get('content')) > 50 else messages[0].get('content')
    
    if not preview:
        preview = '开始一个新的对话...'
    
    try:
        # 创建新对话
        conversation_data = {
            'user_id': user_id,
            'title': title,
            'preview': preview,
            'messages': messages,
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        conversation = create('conversations', conversation_data)
        
        return jsonify({
            'message': 'Conversation created successfully',
            'conversation': conversation
        }), 201
    except Exception as e:
        print(f"Error creating conversation: {str(e)}")
        return jsonify({'error': 'Failed to create conversation'}), 500

# 更新对话
@conversation_bp.route('/<conversation_id>', methods=['PUT'])
@token_required
def update_conversation(current_user, conversation_id):
    user_id = current_user.get('id')
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 检查对话是否属于当前用户
    conversations = query('conversations', {'id': f'conversations:{conversation_id}'})
    if not conversations or len(conversations) == 0:
        return jsonify({'error': 'Conversation not found'}), 404
    
    conversation = conversations[0]
    if conversation.get('user_id') != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # 准备更新数据
    update_data = {}
    
    if 'title' in data:
        update_data['title'] = data['title']
    
    if 'messages' in data:
        update_data['messages'] = data['messages']
        
        # 更新预览文本
        preview = ''
        messages = data['messages']
        if messages and len(messages) > 0:
            for msg in messages:
                if msg.get('role') == 'assistant' and msg.get('content'):
                    preview = msg.get('content')[:50] + '...' if len(msg.get('content')) > 50 else msg.get('content')
                    break
            
            if not preview and messages[0].get('content'):
                preview = messages[0].get('content')[:50] + '...' if len(messages[0].get('content')) > 50 else messages[0].get('content')
        
        if preview:
            update_data['preview'] = preview
    
    # 更新最后修改时间
    update_data['last_updated'] = datetime.utcnow().isoformat()
    
    try:
        # 更新对话
        updated_conversation = update('conversations', conversation_id, update_data)
        
        return jsonify({
            'message': 'Conversation updated successfully',
            'conversation': updated_conversation
        }), 200
    except Exception as e:
        print(f"Error updating conversation: {str(e)}")
        return jsonify({'error': 'Failed to update conversation'}), 500

# 删除对话
@conversation_bp.route('/<conversation_id>', methods=['DELETE'])
@token_required
def delete_conversation(current_user, conversation_id):
    user_id = current_user.get('id')
    
    # 检查对话是否属于当前用户
    conversations = query('conversations', {'id': f'conversations:{conversation_id}'})
    if not conversations or len(conversations) == 0:
        return jsonify({'error': 'Conversation not found'}), 404
    
    conversation = conversations[0]
    if conversation.get('user_id') != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # 删除对话
        from app.db import run_async, get_db
        
        async def _delete():
            db = await get_db()
            if db is None:
                return False
            
            await db.delete(f"conversations:{conversation_id}")
            return True
        
        result = run_async(_delete())
        
        if result:
            return jsonify({
                'message': 'Conversation deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete conversation'}), 500
    except Exception as e:
        print(f"Error deleting conversation: {str(e)}")
        return jsonify({'error': 'Failed to delete conversation'}), 500
