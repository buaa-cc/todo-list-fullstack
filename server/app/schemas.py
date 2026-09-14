"""
schemas.py —— 请求体 / 响应体的数据结构（Pydantic 模型）
职责：定义"前端发过来的 JSON 长什么样"和"后端返回的 JSON 长什么样"，
     并自动做类型校验。校验不通过 FastAPI 会直接返回 422，不用自己写 if 判断。

注意区别：
  models.py  描述「数据库表」——怎么存
  schemas.py 描述「接口数据」——怎么传
两者分开，以后接口字段变了不会连累表结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """POST /todos 的请求体：新建时只需要传 text"""

    # Field(...) 的 ... 表示必填；min_length/max_length 自动校验长度
    text: str = Field(..., min_length=1, max_length=200, description="任务内容")


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 的请求体：两个字段都可选，只改传上来的那些"""

    text: Optional[str] = Field(None, min_length=1, max_length=200)
    done: Optional[bool] = None


class TodoOut(BaseModel):
    """响应体：返回给前端的一条任务"""

    id: int
    text: str
    done: bool
    created_at: datetime
    updated_at: datetime

    # 允许把 SQLAlchemy 的对象直接当这个模型用（否则要手动转 dict）
    model_config = {"from_attributes": True}
