"""
models.py —— 数据表定义（ORM 模型）
职责：用 Python 类描述数据库表。一个类 = 一张表，一个属性 = 一个字段。
启动时 SQLAlchemy 会根据这些类自动建表（如果表还不存在）。
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


class Todo(Base):
    """待办事项表"""

    __tablename__ = "todos"

    # primary_key=True 主键；autoincrement=True 自增，插入时不用自己给值
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # String(200) 对应 VARCHAR(200)；nullable=False 表示不许为空
    text = Column(String(200), nullable=False)

    # 布尔值，用 0/1 存。default=False 表示不传就当未完成
    done = Column(Boolean, nullable=False, default=False)

    # default 只在「插入」时生效
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # onupdate 在「每次更新」时自动刷新，用来记录最后修改时间
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def __repr__(self) -> str:
        # 调试时 print(obj) 能看到内容，不影响运行
        return f"<Todo id={self.id} text={self.text!r} done={self.done}>"
