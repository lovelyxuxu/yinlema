# 鹿了么（lulemo）

[![Vue](https://img.shields.io/badge/frontend-Vue%203-%2342b883)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/database-MongoDB-47a248)](https://www.mongodb.com/)

「鹿了么」是一款面向移动端优先体验的 **男性健康自我管理** 辅助工具，以 Web 应用形式帮助你记录与分析个人行为数据，并结合轻松、积极的文案与设计，鼓励自我管理。

本项目采用前后端分离架构，后端提供 REST API，前端为单页应用，可部署在自建环境或与主站 Nginx 统一入口托管。

---

## ✨ 主要功能

| 模块 | 说明 |
|------|------|
| **鹿了么** | 行为记录列表与统计，支持按天 / 周 / 月等维度查看；结合历史数据给出参考与鼓励性提示（如已连续多少天未发生记录等）。 |
| **今日鹿么** | 通过随机结果为「今日是否发生」给出趣味互动，附带对应文案反馈。 |
| **身份** | 可切换不同「角色」设定如西格玛男人、混沌乐子人等，从而影响「今日鹿么」环节的随机倾向（例如高自律角色对应极低概率）。 |

> 产品文档中对领域用语有约定：对外或面向用户的表述使用「鹿」等隐喻，代码中与数据模型建议使用清晰、可维护的命名加以区分。

---

## 🛠 技术栈

- **前端**：[Vue 3](https://vuejs.org/) · [Vue Router](https://router.vuejs.org/) · [Vite](https://vite.dev/) · TypeScript
- **后端**：[FastAPI](https://fastapi.tiangolo.com/) · [Motor](https://motor.readthedocs.io/)（异步 MongoDB）· JWT 鉴权
- **数据存储**：MongoDB

更详细的后端目录说明与 API 列表见 [`serve/README.md`](serve/README.md)。

---

## 📁 仓库结构

```
lulemo/
├── web/                 # 前端（Vite + Vue 3）
├── serve/               # 后端（FastAPI）
│   ├── app/             # 应用代码
│   ├── scripts/         # 初始化脚本等
│   └── doc/             # 后端设计文档
├── doc/                 # 产品 / 需求说明
├── docker-compose.yml   # 后端 + MongoDB 编排（可与主站 Docker 网络联动）
└── README.md
```

---

## 🚀 本地开发

### 环境要求

- Node.js 18+（建议 LTS）
- Python 3.11+（与 `serve` 依赖兼容即可）
- MongoDB（本地或 Docker）

### 1. 启动后端

```bash
cd serve
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env：至少设置 SECRET_KEY、MONGODB_URL、ALLOWED_ORIGINS
```

确保 MongoDB 可访问（默认示例为 `mongodb://localhost:27020`，见 `serve/.env.example`）。然后：

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger：http://localhost:8000/docs  
- 健康检查：http://localhost:8000/

（可选）初始化含历史数据的测试账号，详见 `serve/README.md` 中的说明。

### 2. 启动前端

```bash
cd web
npm install
cp .env.example .env
# 默认 VITE_API_URL 指向 http://localhost:8000/api/v1
npm run dev
```

开发服务器一般为 http://localhost:5173 ，请保证 `serve/.env` 里 `ALLOWED_ORIGINS` 包含该地址。

### 3. 生产构建（前端）

```bash
cd web
npm run build
```

生产环境 API 基址由 `web/.env.production` 中的 `VITE_API_URL` 决定（例如经主站 Nginx 的 `/lulemo-api/` 前缀代理）。

---

## 🐳 Docker Compose

根目录 [`docker-compose.yml`](docker-compose.yml) 提供 **MongoDB + 后端** 的编排示例。

- **与主站联动**：注释中说明需先启动主项目（如 `COWebsite`）以创建共享网络 `bolt_net`，再由 Nginx 反代到容器 `lulemo-backend:8000`。
- **独立调试**：可按该文件顶部的注释，将后端端口映射到本机并临时调整网络配置。

使用前请在 `serve/` 下准备好 `.env`（可从 `serve/.env.example` 复制并修改）。

---

## 📖 更多文档

- 产品说明：[doc/鹿了么.md](doc/鹿了么.md)
- 后端 API 与目录：[serve/README.md](serve/README.md)
- 接口设计细节：[serve/doc/设计文档.md](serve/doc/设计文档.md)

---

## 🤝 参与贡献

欢迎通过 Issue / Pull Request 提出建议或提交改进。提交前请保持变更与现有代码风格一致，并避免在仓库中提交密钥、真实账号数据等敏感信息。

---

## ⚠️ 免责声明

本工具仅作为个人记录与自我管理的辅助参考，**不能替代**专业医疗建议。如有健康方面的疑虑，请咨询正规医疗机构或专业人员。
