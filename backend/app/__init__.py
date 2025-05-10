from flask import Flask
from flask_cors import CORS  # 导入 CORS


def create_app():
    app = Flask(__name__)
    # 详细配置CORS，允许所有必要的跨域请求
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    from .routes.ai_routes import ai_bp
    from .routes.relationship_routes import relationship_bp  # 导入关系路由
    from .routes.chat_routes import chat_bp  # 导入聊天路由
    # from .routes.auth_routes import auth_bp  # 如果有认证路由
    # from .routes.user_routes import user_bp  # 如果有用户路由

    app.register_blueprint(ai_bp)
    app.register_blueprint(relationship_bp)  # 注册关系路由
    app.register_blueprint(chat_bp)  # 注册聊天路由
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)

    return app


app = create_app()