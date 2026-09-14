"""
database.py —— 数据库连接层
职责：创建数据库引擎、提供会话（Session）、提供 ORM 基类。
整个项目里"连哪个数据库"只在这一个文件里决定。
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# __file__ 是这个文件本身的绝对路径
# os.path.dirname 取上一级 = app/ 目录，再取上一级 = server/ 目录
# 这样无论从哪个目录启动服务，数据库文件都固定生成在 server/todos.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "todos.db")

# ---------- 数据库地址 ----------
# 默认用 SQLite：零安装，就是一个本地文件，适合开发阶段
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 以后要换成 MySQL，只需要把上面那行注释掉、换成下面这行：
#   pip install pymysql
#   DATABASE_URL = "mysql+pymysql://root:你的密码@127.0.0.1:3306/todo?charset=utf8mb4"
# 其余代码一行都不用改 —— 这就是用 ORM 的好处

# SQLite 有个限制：默认不允许跨线程使用同一个连接。
# FastAPI 处理每个请求用的是线程池，所以要关掉这个检查。
# 换成 MySQL 时这个参数不需要，可以删掉 connect_args。
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 引擎：真正负责和数据库通信的对象
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 会话工厂：每次请求要一个独立的 Session（可以理解成"一次数据库对话"）
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 所有表定义的基类，models.py 里的类都继承它
Base = declarative_base()


def get_db():
    """
    依赖注入用的生成器：FastAPI 会在每个请求进来时调用它拿一个 Session，
    请求结束后自动执行 finally 把连接关掉。
    这样业务代码里就不用自己管开关连接了。
    """
    db = SessionLocal()
    try:
        yield db          # yield 之前是"请求开始"，之后是"请求结束"
    finally:
        db.close()
