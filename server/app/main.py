"""
main.py —— 应用入口 + 路由
职责：创建 FastAPI 应用、挂 CORS 中间件、定义 5 个 REST 接口。

启动：在 server/ 目录下执行
    uvicorn app.main:app --reload
然后把浏览器打开 http://127.0.0.1:8000/docs 就能看到自动生成的接口文档。
"""

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

# 建表：检查 models 里声明的所有表，缺失的就创建。
# 已存在的表不会被改动（所以改字段要自己处理迁移，初学阶段直接删 todos.db 重建即可）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo List API",
    description="待办事项应用的后端接口",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS：浏览器的同源策略默认禁止网页请求"别的域名+端口"。
# 前端跑在 http://localhost:5173，后端在 http://localhost:8000，
# 属于跨域，所以要在后端声明"允许这个来源访问"。
# 不配的话浏览器控制台会报 CORS 错误，但用 curl 测是正常的 —— 这是新手最容易卡住的坑。
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 1) 查列表
#    GET /todos            返回全部
#    GET /todos?done=true  只返回已完成的
# ---------------------------------------------------------------------------
@app.get("/todos", response_model=List[schemas.TodoOut], summary="获取任务列表")
def list_todos(done: Optional[bool] = None, db: Session = Depends(get_db)):
    # db.query(Todo) 相当于 SELECT * FROM todos
    query = db.query(models.Todo)

    # 传了 done 参数才加过滤条件
    if done is not None:
        query = query.filter(models.Todo.done == done)

    # 按创建时间倒序，最新的排前面
    return query.order_by(models.Todo.created_at.desc()).all()


# ---------------------------------------------------------------------------
# 2) 新建
#    POST /todos   body: {"text": "写作业"}
# ---------------------------------------------------------------------------
@app.post(
    "/todos",
    response_model=schemas.TodoOut,
    status_code=status.HTTP_201_CREATED,   # 201 = 创建成功（不是 200）
    summary="新建任务",
)
def create_todo(payload: schemas.TodoCreate, db: Session = Depends(get_db)):
    # payload 已经被 Pydantic 校验过了，这里 text 一定是 1~200 字的字符串
    todo = models.Todo(text=payload.text)

    db.add(todo)        # 放进会话，准备插入
    db.commit()         # 提交事务，真正写进数据库
    db.refresh(todo)    # 回读一次，拿到数据库生成的 id / created_at

    return todo


# ---------------------------------------------------------------------------
# 3) 查单条
#    GET /todos/1
# ---------------------------------------------------------------------------
@app.get("/todos/{todo_id}", response_model=schemas.TodoOut, summary="获取单条任务")
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    # 路径里的 {todo_id} 由 FastAPI 自动转成 int，传 "abc" 会直接返回 422
    todo = db.get(models.Todo, todo_id)

    if todo is None:
        # 404 = 资源不存在
        raise HTTPException(status_code=404, detail=f"任务 {todo_id} 不存在")

    return todo


# ---------------------------------------------------------------------------
# 4) 局部更新（勾选完成 / 改文字）
#    PATCH /todos/1   body: {"done": true}
#    PATCH /todos/1   body: {"text": "新内容"}
# ---------------------------------------------------------------------------
@app.patch("/todos/{todo_id}", response_model=schemas.TodoOut, summary="更新任务")
def update_todo(
    todo_id: int,
    payload: schemas.TodoUpdate,
    db: Session = Depends(get_db),
):
    todo = db.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"任务 {todo_id} 不存在")

    # exclude_unset=True 的含义：只取出前端"确实传了"的字段。
    # 这样前端只传 {"done": true} 时，text 保持原样不会被覆盖成 None
    changes = payload.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


# ---------------------------------------------------------------------------
# 5) 删除
#    DELETE /todos/1
# ---------------------------------------------------------------------------
@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,   # 204 = 成功但没有响应体
    summary="删除任务",
)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"任务 {todo_id} 不存在")

    db.delete(todo)
    db.commit()
    # 返回 None，FastAPI 配合 204 状态码不会输出任何 body
    return None


# ---------------------------------------------------------------------------
# 健康检查：部署到服务器后用它确认服务活着
# ---------------------------------------------------------------------------
@app.get("/health", summary="健康检查")
def health():
    return {"status": "ok"}
