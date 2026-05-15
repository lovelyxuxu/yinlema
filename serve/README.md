# 鹿了么 · 后端服务

基于 **FastAPI + MongoDB** 的后端 API 服务。

## 目录结构

```
serve/
├── app/
│   ├── core/
│   │   ├── config.py       # 环境配置（pydantic-settings）
│   │   ├── database.py     # MongoDB 异步连接（motor）
│   │   └── security.py     # 密码哈希 & JWT 工具
│   ├── models/
│   │   ├── user.py         # 用户 MongoDB 文档模型
│   │   └── record.py       # 鹿记录 MongoDB 文档模型
│   ├── schemas/
│   │   ├── auth.py         # 注册/登录请求与响应 Schema
│   │   ├── user.py         # 用户信息 Schema
│   │   └── record.py       # 记录相关 Schema
│   ├── routers/
│   │   ├── auth.py         # POST /auth/register, POST /auth/login, GET /auth/me
│   │   ├── users.py        # PUT /users/me/identity
│   │   └── records.py      # CRUD /records & GET /records/stats
│   ├── deps.py             # FastAPI 依赖注入（鉴权）
│   └── main.py             # 应用入口
├── doc/                    # 设计文档
├── scripts/                # 数据库脚本（初始化测试数据等）
├── requirements.txt
├── .env.example
└── README.md
```

## 快速启动

### 1. 安装依赖

```bash
cd serve
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，修改 SECRET_KEY 等配置
```

### 3. 启动 MongoDB

确保本地 MongoDB 已运行（默认 `mongodb://localhost:27020`），或修改 `.env` 中的 `MONGODB_URL`。
推荐使用docker容器：docker run -d --name lulemo-mongodb -p 27020:27017 mongo

### 4. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

启动后访问：
- API 文档（Swagger）：http://localhost:8000/docs
- API 文档（ReDoc）：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/

### 5. 数据库脚本（可选）

在 **`scripts/`** 目录提供 MongoDB 初始化脚本。

初始化测试账号 **`luwang` / `88888888`**，并写入约 **90 天**随机分布的历史鹿记录（重复执行会先删掉同名旧账号及其记录再重建）：

```bash
cd serve
python scripts/init_test_user.py
```

## API 概览

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/v1/auth/register | 注册账号 | 否 |
| POST | /api/v1/auth/login | 账号登录 | 否 |
| GET  | /api/v1/auth/me | 获取当前用户信息 | 是 |
| PUT  | /api/v1/users/me/identity | 更新身份角色 | 是 |
| GET  | /api/v1/records | 获取鹿记录列表 | 是 |
| POST | /api/v1/records | 新增鹿记录 | 是 |
| DELETE | /api/v1/records/{id} | 删除鹿记录 | 是 |
| GET  | /api/v1/records/stats | 获取统计数据 | 是 |

详细接口文档见 [doc/设计文档.md](doc/设计文档.md)。
