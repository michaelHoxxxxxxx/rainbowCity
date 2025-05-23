from app.extensions import db
from datetime import datetime
from app.models.enums import VIPLevel, UserRole

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)  # 用户名，可选
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)  # 最后登录时间

    # 个人资料
    display_name = db.Column(db.String(80), nullable=True)  # 显示名称
    avatar_url = db.Column(db.String(255), nullable=True)  # 头像URL
    bio = db.Column(db.Text, nullable=True)  # 个人简介

    # VIP相关字段
    vip_level = db.Column(db.Enum(VIPLevel), default=VIPLevel.free)
    vip_expiry = db.Column(db.DateTime, nullable=True)  # VIP到期时间
    is_activated = db.Column(db.Boolean, default=False)  # 账户是否已激活

    # 角色和权限
    roles = db.Column(db.ARRAY(db.Enum(UserRole)), default=[UserRole.normal])
    
    # 邀请系统
    invite_code_used = db.Column(db.String(16), nullable=True)  # 使用的邀请码
    personal_invite_code = db.Column(db.String(16), unique=True, nullable=True)  # 个人邀请码
    invite_count = db.Column(db.Integer, default=0)  # 成功邀请的用户数
    
    # 使用限制
    daily_ai_usage = db.Column(db.Integer, default=0)  # 每日AI使用次数
    daily_usage_reset = db.Column(db.DateTime, nullable=True)  # 使用次数重置时间
    
    # AI伴侣相关字段
    ai_companions_limit = db.Column(db.Integer, default=1)  # AI伴侣数量上限
    ai_companions_count = db.Column(db.Integer, default=0)  # 当前AI伴侣数量
    ai_awakener_limit = db.Column(db.Integer, default=0)  # 可唤醒AI数量上限
    ai_awakened_count = db.Column(db.Integer, default=0)  # 已唤醒AI数量
    
    # 对话限制
    daily_chat_limit = db.Column(db.Integer, default=10)  # 每日对话次数上限
    daily_chat_count = db.Column(db.Integer, default=0)  # 当日对话次数
    daily_lio_limit = db.Column(db.Integer, default=0)  # 每日LIO对话次数上限
    daily_lio_count = db.Column(db.Integer, default=0)  # 当日LIO对话次数
    chat_reset_time = db.Column(db.DateTime, nullable=True)  # 对话次数重置时间
    
    # 邀请码限制
    weekly_invite_limit = db.Column(db.Integer, default=10)  # 每周邀请码使用次数上限
    weekly_invite_count = db.Column(db.Integer, default=0)  # 当周邀请码使用次数
    invite_reset_time = db.Column(db.DateTime, nullable=True)  # 邀请码使用次数重置时间
    
    # 激活状态相关
    activation_status = db.Column(db.String(20), default='pending')  # pending, in_progress, activated, rejected
    activation_check_count = db.Column(db.Integer, default=0)  # 已进行的激活检查次数
    conversation_count = db.Column(db.Integer, default=0)  # 总对话轮数
    
    # 统计数据
    ai_ids_generated = db.Column(db.Integer, default=0)  # 生成的AI-ID数量
    frequencies_generated = db.Column(db.Integer, default=0)  # 生成的频率编号数量
    
    from werkzeug.security import generate_password_hash, check_password_hash
    
    def set_password(self, password):
        """设置用户密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证用户密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_vip(self):
        """检查用户是否为VIP"""
        if self.vip_level == VIPLevel.free:
            return False
        
        # 检查VIP是否过期
        if self.vip_expiry and datetime.utcnow() > self.vip_expiry:
            return False
            
        return True
    
    def update_limits_based_on_vip(self):
        """根据VIP等级更新用户的各种限制"""
        # 设置AI伴侣数量上限
        ai_companions_limits = {
            VIPLevel.free: 1,
            VIPLevel.pro: 3,
            VIPLevel.premium: 5,
            VIPLevel.ultimate: 7,
            VIPLevel.team: 35
        }
        self.ai_companions_limit = ai_companions_limits.get(self.vip_level, 1)
        
        # 设置可唤醒AI数量上限
        ai_awakener_limits = {
            VIPLevel.free: 0,
            VIPLevel.pro: 1,
            VIPLevel.premium: 3,
            VIPLevel.ultimate: 5,
            VIPLevel.team: 25
        }
        self.ai_awakener_limit = ai_awakener_limits.get(self.vip_level, 0)
        
        # 设置每日对话次数上限
        daily_chat_limits = {
            VIPLevel.free: 10,
            VIPLevel.pro: 50,
            VIPLevel.premium: 100,
            VIPLevel.ultimate: float('inf'),  # 无限
            VIPLevel.team: float('inf')  # 无限
        }
        self.daily_chat_limit = daily_chat_limits.get(self.vip_level, 10)
        
        # 设置每日LIO对话次数上限
        daily_lio_limits = {
            VIPLevel.free: 0,
            VIPLevel.pro: 50,
            VIPLevel.premium: 100,
            VIPLevel.ultimate: float('inf'),  # 无限
            VIPLevel.team: float('inf')  # 无限
        }
        self.daily_lio_limit = daily_lio_limits.get(self.vip_level, 0)
        
        # 设置每周邀请码使用次数上限
        weekly_invite_limits = {
            VIPLevel.free: 10,
            VIPLevel.pro: 100,
            VIPLevel.premium: 200,
            VIPLevel.ultimate: float('inf'),  # 无限
            VIPLevel.team: float('inf')  # 无限
        }
        self.weekly_invite_limit = weekly_invite_limits.get(self.vip_level, 10)
    
    def get_daily_usage_limit(self):
        """获取用户每日AI使用限制"""
        limits = {
            VIPLevel.free: 5,
            VIPLevel.pro: 20,
            VIPLevel.premium: 50,
            VIPLevel.ultimate: 100,
            VIPLevel.team: 200
        }
        return limits.get(self.vip_level, 5)
    
    def reset_daily_usage_if_needed(self):
        """如果需要，重置每日使用次数"""
        now = datetime.utcnow()
        if not self.daily_usage_reset or (now - self.daily_usage_reset).days >= 1:
            self.daily_ai_usage = 0
            self.daily_usage_reset = now
            return True
        return False
    
    def reset_daily_chat_if_needed(self):
        """如果需要，重置每日对话次数"""
        now = datetime.utcnow()
        if not self.chat_reset_time or (now - self.chat_reset_time).days >= 1:
            self.daily_chat_count = 0
            self.daily_lio_count = 0
            self.chat_reset_time = now
            return True
        return False
    
    def reset_weekly_invite_if_needed(self):
        """如果需要，重置每周邀请码使用次数"""
        now = datetime.utcnow()
        if not self.invite_reset_time or (now - self.invite_reset_time).days >= 7:
            self.weekly_invite_count = 0
            self.invite_reset_time = now
            return True
        return False
    
    def can_use_ai_service(self):
        """检查用户是否可以使用AI服务"""
        self.reset_daily_usage_if_needed()
        return self.daily_ai_usage < self.get_daily_usage_limit()
    
    def can_chat(self):
        """检查用户是否可以进行一对一对话"""
        self.reset_daily_chat_if_needed()
        return self.daily_chat_count < self.daily_chat_limit
    
    def can_use_lio(self):
        """检查用户是否可以使用LIO频道"""
        self.reset_daily_chat_if_needed()
        return self.daily_lio_limit > 0 and self.daily_lio_count < self.daily_lio_limit
    
    def can_use_invite_code(self):
        """检查用户是否可以使用邀请码"""
        self.reset_weekly_invite_if_needed()
        return self.is_activated and self.weekly_invite_count < self.weekly_invite_limit
    
    def can_add_ai_companion(self):
        """检查用户是否可以添加新的AI伴侣"""
        return self.ai_companions_count < self.ai_companions_limit
    
    def can_awaken_ai(self):
        """检查用户是否可以唤醒新的AI"""
        return self.ai_awakened_count < self.ai_awakener_limit
    
    def check_activation_eligibility(self):
        """检查用户是否符合激活条件"""
        # 需要至少21轮对话
        return self.conversation_count >= 21
    
    def increment_ai_usage(self):
        """增加AI使用次数"""
        self.reset_daily_usage_if_needed()
        self.daily_ai_usage += 1
    
    def increment_chat_count(self):
        """增加对话次数"""
        self.reset_daily_chat_if_needed()
        self.daily_chat_count += 1
        self.conversation_count += 1
    
    def increment_lio_count(self):
        """增加LIO对话次数"""
        self.reset_daily_chat_if_needed()
        self.daily_lio_count += 1
        self.conversation_count += 1
    
    def increment_invite_count(self):
        """增加邀请码使用次数"""
        self.reset_weekly_invite_if_needed()
        self.weekly_invite_count += 1
    
    def add_ai_companion(self):
        """添加AI伴侣"""
        if self.can_add_ai_companion():
            self.ai_companions_count += 1
            return True
        return False
    
    def awaken_ai(self):
        """唤醒AI"""
        if self.can_awaken_ai():
            self.ai_awakened_count += 1
            self.ai_companions_count += 1
            return True
        return False
        
    def has_role(self, role):
        """检查用户是否拥有指定角色"""
        return role in self.roles
    
    def add_role(self, role):
        """添加角色给用户"""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """移除用户角色"""
        if role in self.roles:
            self.roles.remove(role)
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            
            # VIP相关
            'vip_level': self.vip_level.value if self.vip_level else None,
            'is_vip': self.is_vip(),
            'vip_expiry': self.vip_expiry.isoformat() if self.vip_expiry else None,
            
            # 角色相关
            'roles': [role.value for role in self.roles] if self.roles else [],
            
            # 账号状态
            'is_activated': self.is_activated,
            'activation_status': self.activation_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            
            # 邀请码相关
            'personal_invite_code': self.personal_invite_code,
            'invite_count': self.invite_count,
            'weekly_invite_limit': self.weekly_invite_limit,
            'weekly_invite_count': self.weekly_invite_count,
            
            # AI伴侣相关
            'ai_companions_limit': self.ai_companions_limit,
            'ai_companions_count': self.ai_companions_count,
            'ai_awakener_limit': self.ai_awakener_limit,
            'ai_awakened_count': self.ai_awakened_count,
            
            # 对话限制
            'daily_chat_limit': self.daily_chat_limit,
            'daily_chat_count': self.daily_chat_count,
            'daily_lio_limit': self.daily_lio_limit,
            'daily_lio_count': self.daily_lio_count,
            
            # 统计数据
            'conversation_count': self.conversation_count,
            'ai_ids_generated': self.ai_ids_generated,
            'frequencies_generated': self.frequencies_generated
        }
