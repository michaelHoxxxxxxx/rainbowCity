from app import app
from app.db import init_db
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化数据库
init_db(app)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)  # 允许从任何 IP 访问