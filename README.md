# 瘾了吗（yinlema）

[![Vue](https://img.shields.io/badge/frontend-Vue%203-%2342b883)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/database-MongoDB-47a248)](https://www.mongodb.com/)

「瘾了吗」是内部使用的 **健康管理平台**（移动端 Web 优先），V1 主打女性自我管理：按次记录、统计「没瘾天数」与「上次翻车至今」，保留社交排行（出动率 / 瘾次）、今日检定与人设等轻松玩法。

设计规格：[docs/superpowers/specs/2026-05-23-yinlema-design.md](docs/superpowers/specs/2026-05-23-yinlema-design.md)  
实现计划：[docs/superpowers/plans/2026-05-23-yinlema.md](docs/superpowers/plans/2026-05-23-yinlema.md)

---

## 主要功能

| 模块 | 说明 |
|------|------|
| **瘾了吗** | 又瘾了 / 补记、列表与图表、双指标横幅 |
| **今日检定** | 随机趣味（不写库） |
| **人设** | 影响检定瘾运 |
| **社交** | 排名、广场、小队 |

---

## 技术栈

- **前端**：Vue 3 · Vue Router · Vite · TypeScript
- **后端**：FastAPI · Motor · JWT
- **数据**：MongoDB（库名默认 `yinlema`）

---

## 本地开发

### 后端

```bash
cd serve
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest tests/ -v   # PYTHONPATH=. 或在 serve 目录下执行
```

### 前端

```bash
cd web
npm install
cp .env.example .env
npm run dev
```

### 迁移（从旧 check_ins）

```bash
cd serve
python scripts/migrate_check_ins_to_records.py
```

---

## Docker

见 [`docker-compose.yml`](docker-compose.yml)（服务名 `yinlema-*`）。

---

## 免责声明

内部工具，记录仅供参考，不能替代医疗建议。
