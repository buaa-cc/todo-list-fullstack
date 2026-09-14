# Todo List 后端（FastAPI + SQLite）

这是给 `my-vue-app` 前端配的后端。加完之后项目从「纯前端玩具」变成
**前后端分离 + 数据库持久化**的完整应用：关掉浏览器再打开，任务还在。

---

## 一、怎么跑起来（两步）

### 1. 装依赖（只做一次）

在 `server/` 目录下打开终端：

```bash
# 创建虚拟环境（避免把包装到系统 Python 里）
python -m venv .venv

# 激活（Windows Git Bash / PowerShell）
source .venv/Scripts/activate      # Git Bash
.venv\Scripts\activate             # PowerShell / CMD

# 装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 必须在 server/ 目录下执行
uvicorn app.main:app --reload
```

看到 `Uvicorn running on http://127.0.0.1:8000` 就成了。

- **接口文档（自动生成，可直接点按钮测试）**：http://127.0.0.1:8000/docs
- `--reload` 表示改代码后服务自动重启，开发时必备。

### 3. 启动前端（另开一个终端）

```bash
# 在 my-vue-app 根目录
npm run dev
```

打开 http://localhost:5173 就能用了。

---

## 二、文件结构与各自职责

```
server/
├── requirements.txt      依赖清单
├── todos.db              SQLite 数据库文件（首次启动自动生成）
└── app/
    ├── __init__.py       声明 app 是一个包
    ├── database.py       数据库连接：连哪个库、怎么拿会话
    ├── models.py         表结构：一个类 = 一张表
    ├── schemas.py        接口数据格式：请求体/响应体长什么样 + 校验
    └── main.py           应用入口 + 5 个接口
```

**为什么要拆这几个文件？** 核心原则是**分层**：数据库怎么存、接口怎么传、
业务怎么处理，三者分开。以后换 MySQL 只改 `database.py`，改接口字段只改
`schemas.py`，互不影响。全都堆在一个文件里，几十行之后就没法维护了。

---

## 三、数据表设计

```sql
CREATE TABLE todos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增
    text       VARCHAR(200) NOT NULL,              -- 任务内容，必填
    done       BOOLEAN NOT NULL DEFAULT 0,         -- 是否完成
    created_at DATETIME NOT NULL,                  -- 创建时间
    updated_at DATETIME NOT NULL                   -- 最后修改时间
);
```

说明几个设计上的考虑：

- **`id` 自增主键**：业务上不需要自己编号，交给数据库生成，最省事。
- **为什么加 `done` 而不是直接删掉已完成任务**：状态比存在性表达力强，
  以后想加"只看未完成"、统计完成率都靠它。
- **`created_at` / `updated_at`**：排查问题时的第一手线索，几乎每个表都该有。
  前者在插入时写一次，后者每次更新自动刷新（靠 SQLAlchemy 的 `onupdate`）。
- **`NOT NULL` 尽量都加上**：让数据库兜住脏数据，比在代码里到处判空可靠。

---

## 四、接口设计（REST 风格）

| 方法 | 路径 | 作用 | 请求体 | 成功状态码 |
|---|---|---|---|---|
| GET | `/todos` | 查列表，`?done=true` 可筛选 | — | 200 |
| POST | `/todos` | 新建一条 | `{"text": "..."}` | 201 |
| GET | `/todos/{id}` | 查单条 | — | 200 |
| PATCH | `/todos/{id}` | 局部更新 | `{"done": true}` 或 `{"text": "..."}` | 200 |
| DELETE | `/todos/{id}` | 删除 | — | 204 |
| GET | `/health` | 健康检查（部署后探活用） | — | 200 |

### 几个新手容易搞错的地方

- **为什么新建返回 201 不是 200**：HTTP 语义里 201 = Created，
  明确表示"资源被创建了"。200 是通用成功。用对了显得懂行。
- **为什么删除返回 204**：204 = 成功但没有响应体。所以前端拿到 204 时
  **不能调 `res.json()`**，会抛异常 —— 前端代码里专门判了这一条。
- **为什么更新用 PATCH 而不是 PUT**：PUT 语义是整体替换（没传的字段会被清空），
  PATCH 是局部修改。我们的场景是"只改一个勾选状态"，所以用 PATCH。
- **`?done=true` 这种叫查询参数**，出现在路径 `?` 后面；
  `/todos/{id}` 里的 `id` 叫路径参数。两者用途不同：前者用来筛选，
  后者用来定位唯一资源。

---

## 五、逐个文件讲代码

### `database.py`

```python
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
```

- **engine（引擎）**：管理连接池，程序里只有一个，全局共享。
- **SessionLocal（会话工厂）**：一次数据库操作 = 一个 Session。
  它是"工厂"不是"会话本身"，每次调用 `SessionLocal()` 才产出一个会话。
  类比：`engine` 是水池，`Session` 是接水的水杯。
- **`get_db()` 里的 `yield`**：这是 FastAPI 的**依赖注入**。请求进来时执行
  `yield db` 之前的部分（开会话），请求结束时执行 `finally`（关会话）。
  所以业务函数里永远不用写 `db.close()`，不会漏关连接。

`autocommit=False` 意味着**必须手动 `commit()`**，这是好事：一件事没做完
不会写进库，出错了也不会留下半截数据。

### `models.py`

用类描述表。`Column(...)` 的每个参数就是列的定义：

```python
text = Column(String(200), nullable=False)              # 非空字符串，最长 200
done = Column(Boolean, nullable=False, default=False)   # default 只在插入时生效
updated_at = Column(..., onupdate=datetime.now)         # 每次 UPDATE 自动刷新
```

注意 **`default` 和 `onupdate` 的区别**：前者管"插入时给什么值"，
后者管"更新时自动改成什么"。`updated_at` 两个都写了，所以插入和更新都会填。

### `schemas.py`

**models.py 管"怎么存"，schemas.py 管"怎么传"**，这是两个不同的关注点：
数据库字段以后可能加内部用的列（比如 `is_deleted`），但不该暴露给前端；
反过来前端可能需要组合字段（比如 `text_with_id`），也不该建到表里。

```python
text: str = Field(..., min_length=1, max_length=200)
```

这一行同时干了三件事：声明类型是字符串、声明必填（`...`）、声明长度范围。
**校验失败 FastAPI 自动返回 422**，不用自己写 `if not text: return error`。

`model_config = {"from_attributes": True}` 让 SQLAlchemy 对象能直接当响应用，
否则要手动 `{"id": t.id, "text": t.text, ...}` 一个个转。

### `main.py`

```python
@app.get("/todos", response_model=List[schemas.TodoOut], summary="获取任务列表")
def list_todos(done: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(models.Todo)
    if done is not None:
        query = query.filter(models.Todo.done == done)
    return query.order_by(models.Todo.created_at.desc()).all()
```

- **装饰器 `@app.get(...)`** 把函数绑到"GET 这个方法 + 这个路径"上。
- **`response_model`** 声明返回结构，FastAPI 会做序列化 + 过滤掉多余字段。
- **`Depends(get_db)`**：声明"我需要一个数据库会话"，由框架注入 —— 这就是
  依赖注入，好处是测试时能换成假会话。
- **`db.query(...)` 是链式的**，可以一直 `.filter().order_by()` 拼下去，
  最后 `.all()` 才真正执行 SQL。不调用 `.all()` / `.first()` 就不会查库。

新建接口里的三步是固定套路：

```python
todo = models.Todo(text=payload.text)  # 1. 建对象（此时还没进数据库）
db.add(todo)                            # 2. 加入会话
db.commit()                             # 3. 提交，真正写库
db.refresh(todo)                        # 4. 回读，拿到数据库生成的 id 和时间
```

`db.refresh(todo)` 这步新手最常忘：不 refresh 的话，返回的 `id` 是 `None`，
因为 id 是数据库生成后才知道的。

更新接口里有个关键细节：

```python
changes = payload.model_dump(exclude_unset=True)
for field, value in changes.items():
    setattr(todo, field, value)
```

**`exclude_unset=True` 必须加**。不加的话，前端只传 `{"done": true}` 时，
`text` 会是 `None`，循环执行 `setattr(todo, "text", None)` 就把内容清掉了。
这是 PATCH 语义的核心：**只改传来的字段**。

### CORS 中间件（前端联调必踩的坑）

```python
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", ...])
```

浏览器有个**同源策略**：网页默认只能请求"同协议 + 同域名 + 同端口"的接口。
前端在 `5173`，后端在 `8000`，端口不同 = 跨域，浏览器会拦。

典型症状：**用 curl 或 Postman 测试一切正常，但网页一调就报 CORS 错误**。
原因就是浏览器在拦，不是后端挂了。解决办法两种：

1. 后端显式声明"允许这个来源"（本项目用的，在 `main.py` 里）；
2. 前端用 Vite 的 proxy 把 `/api` 转发到 8000，绕过跨域（生产环境常用）。

---

## 六、换到 MySQL 要改什么

只改 `database.py` 里的一行：

```python
DATABASE_URL = "mysql+pymysql://root:你的密码@127.0.0.1:3306/todo?charset=utf8mb4"
```

```bash
pip install pymysql
```

然后**删掉 `connect_args`**（`check_same_thread` 是 SQLite 专有的），
MySQL 里先手动建库：`CREATE DATABASE todo DEFAULT CHARSET utf8mb4;`

表会在第一次启动时自动创建。其余代码一行不动 —— 这就是用 ORM 的价值。

---

## 七、下一步可以加什么（按投入产出排序）

1. **参数校验再收紧**：给 `text` 加 `.strip()`，拒绝纯空格。
2. **分页**：`GET /todos?skip=0&limit=20`，数据多了必须有。
3. **统一错误响应**：用 `@app.exception_handler` 把错误格式统一成
   `{"code": ..., "message": ...}`，前端好处理。
4. **加一层 service**：把业务逻辑从路由函数里抽出去，
   路由只负责收参数、返回结果。
5. **部署**：买一台云服务器，用 `nginx` 做反向代理 + `systemd` 或
   `docker` 托管进程。这一步做完，简历上「服务端部署」就是真的了。
