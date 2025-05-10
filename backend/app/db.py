import asyncio
import os
import time
import threading
from flask import g, current_app
import surrealdb
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# SurrealDB配置
SURREAL_URL = os.getenv('SURREAL_URL', 'ws://localhost:8080')
SURREAL_USER = os.getenv('SURREAL_USER', 'root')
SURREAL_PASS = os.getenv('SURREAL_PASS', '123')
SURREAL_NS = os.getenv('SURREAL_NS', 'rainbow')
SURREAL_DB = os.getenv('SURREAL_DB', 'test')

# 全局数据库连接
_db = None
_db_lock = threading.Lock()
_connection_attempts = 0
_max_connection_attempts = 3
_connection_retry_delay = 2  # 秒

# 检查连接是否可用
async def is_connection_alive():
    """检查数据库连接是否正常"""
    global _db
    if _db is None:
        return False
    
    try:
        # 尝试执行一个简单的查询
        await _db.query('INFO FOR DB')
        return True
    except Exception:
        return False

# 初始化数据库连接
async def init_db_connection():
    """初始化数据库连接"""
    global _db, _connection_attempts
    
    # 使用锁确保只有一个线程在初始化连接
    with _db_lock:
        # 如果连接已存在且正常，直接返回
        if _db is not None and await is_connection_alive():
            return _db
        
        # 检查连接尝试次数
        if _connection_attempts >= _max_connection_attempts:
            print(f"Maximum connection attempts ({_max_connection_attempts}) reached. Using mock mode.")
            return None
        
        # 尝试连接
        _connection_attempts += 1
        try:
            # 如果已有连接，先关闭
            if _db is not None:
                try:
                    await _db.close()
                except Exception:
                    pass
            
            # 创建新连接
            _db = surrealdb.Surreal()
            await _db.connect(SURREAL_URL)
            await _db.signin({"user": SURREAL_USER, "pass": SURREAL_PASS})
            await _db.use(SURREAL_NS, SURREAL_DB)
            print(f"Connected to SurrealDB at {SURREAL_URL} (attempt {_connection_attempts})")
            
            # 重置连接尝试计数
            _connection_attempts = 0
            return _db
        except Exception as e:
            print(f"Error connecting to SurrealDB (attempt {_connection_attempts}): {e}")
            
            # 如果还有尝试次数，等待一段时间后重试
            if _connection_attempts < _max_connection_attempts:
                print(f"Retrying in {_connection_retry_delay} seconds...")
                time.sleep(_connection_retry_delay)
                return await init_db_connection()
            
            return None

# 异步获取数据库连接
async def get_db():
    """获取数据库连接"""
    global _db
    
    # 如果连接不存在或者不正常，初始化连接
    if _db is None or not await is_connection_alive():
        return await init_db_connection()
    
    return _db

# 异步关闭数据库连接
async def close_db():
    """关闭数据库连接"""
    global _db
    with _db_lock:
        if _db is not None:
            try:
                await _db.close()
                _db = None
                print("SurrealDB connection closed")
            except Exception as e:
                print(f"Error closing SurrealDB connection: {e}")

# 同步包装器，将异步操作转换为同步操作
def run_async(async_func):
    """运行异步函数并返回结果"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_func)
    finally:
        loop.close()

# 初始化数据库
def init_db(app):
    """初始化数据库"""
    # 在应用启动时初始化数据库连接
    with app.app_context():
        try:
            run_async(init_db_connection())
            print("Database initialized successfully")
        except Exception as e:
            print(f"Failed to initialize database: {e}")
    
    # 注册应用关闭时的回调
    @app.teardown_appcontext
    def teardown_db(exception=None):
        try:
            run_async(close_db())
        except Exception as e:
            print(f"Error in teardown_db: {e}")

# 同步创建数据
def create(table, data):
    """在指定表中创建数据"""
    async def _create():
        db = await get_db()
        if db is None:
            print("Using mock mode for create operation")
            return data
        
        try:
            result = await db.create(table, data)
            return result
        except Exception as e:
            print(f"Error creating data in {table}: {e}")
            return data
    
    return run_async(_create())

# 同步查询数据
def query(table, condition=None):
    """查询指定表中的数据"""
    async def _query():
        db = await get_db()
        if db is None:
            print("Using mock mode for query operation")
            return []
        
        try:
            if condition is None:
                # 查询所有数据
                result = await db.query(f"SELECT * FROM {table}")
            else:
                # 构建条件查询
                conditions = " AND ".join([f"{k} = '{v}'" for k, v in condition.items()])
                result = await db.query(f"SELECT * FROM {table} WHERE {conditions}")
            
            # 处理查询结果
            if result and result[0] and 'result' in result[0]:
                return result[0]['result']
            return []
        except Exception as e:
            print(f"Error querying data from {table}: {e}")
            return []
    
    return run_async(_query())

# 同步更新数据
def update(table, id, data):
    """更新指定表中的数据
    
    Args:
        table (str): 表名
        id (str): 记录ID
        data (dict): 要更新的数据
        
    Returns:
        dict: 更新后的记录
    """
    async def _update():
        db = await get_db()
        if db is None:
            print("Using mock mode for update operation")
            return data
        
        try:
            # 使用SurrealDB的update方法更新记录
            result = await db.update(f"{table}:{id}", data)
            return result
        except Exception as e:
            print(f"Error updating data in {table}: {e}")
            return None
    
    return run_async(_update())