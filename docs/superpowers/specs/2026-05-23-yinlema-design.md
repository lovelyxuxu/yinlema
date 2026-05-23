# 瘾了吗（yinlema）产品设计规格

**日期**：2026-05-23  
**状态**：已评审通过（brainstorming）  
**范围**：将「鹿了么 / lulemo」 rebranding 为平台「瘾了吗」，V1 主打女性自慰频率自我管理（内部使用）。

---

## 1. 背景与目标

### 1.1 现状

- 仓库：`lulemo`，Vue 3 移动端 Web + FastAPI + MongoDB。
- 原定位：男性向「鹿」隐喻的行为记录与趣味互动。
- 已有能力：按条 `records`、每日 `check_ins`、统计图、今日随机、人设、社交（排名 / 匿名广场 / 小队）。

### 1.2 目标

| 项 | 说明 |
|----|------|
| 产品名 | **瘾了吗**（平台级） |
| V1 习惯 | 女性自慰频率自我管理（内部梗文案，偏色轻松，不羞耻） |
| 数据原则 | **方案一**：`records` 为唯一事实来源；一天可多条 |
| 统计展示 | 主：连续未瘾天数；次：上次翻车至今；社交：出动率 / 瘾次 |
| 社交 | 保留全部 V1 社交能力，指标改口径 |
| 工程 | 仓库与配置改名为 **yinlema** |
| 后期 | 并入「鹿了吗」（`deer_male`）、戒烟/戒手机等习惯模块；设置内周目标（原 D 方案） |

### 1.3 非目标（V1）

- 诱因、地点等 `metadata` 表单（仅预留字段）。
- 多习惯切换 UI、分榜。
- 周目标 `weekly_max_events` 配置。
- 对外公开发布 / 合规文案（内部使用）。

---

## 2. 产品定位与架构

### 2.1 平台结构

```text
瘾了吗（yinlema）
├── self_care_female   ← V1 默认且唯一入口
├── deer_male          ← 后期「鹿了吗」
└── quit_*             ← 远期（戒烟、戒手机等）
```

### 2.2 架构决策：记录即真相

- 所有统计、排行均由 `records` 聚合。
- 废弃前端独立打卡；`check_ins` 迁移后 deprecated。
- 今日检定 / 人设：仅趣味，**不写入** `records`。

### 2.3 统计口径（代码层中性命名）

| 概念 | 规则 |
|------|------|
| 有记录日 | 当日 `records` 条数 ≥ 1 |
| `streak_days_no_record` | 从最后一次 `timestamp` 的**下一自然日**起，连续多少个上海日历日 0 条记录 |
| `since_last_ms` | `now - last_record.timestamp` |
| `today_count` | 当日记录条数 |
| 出动率（rate） | 有记录日数 ÷ 统计期天数 |
| 瘾次（count） | 事件总条数 |

---

## 3. 信息架构与交互

### 3.1 底部导航

| Tab | 路由 | 说明 |
|-----|------|------|
| 瘾了吗 | `/` | 指标 + 图表 + 事件列表 |
| 今日检定 | `/today` | 随机趣味 |
| 人设 | `/identity` | 影响检定概率 |
| 社交 | `/social/*` | 排名 / 广场 / 小队 |

### 3.2 主屏「瘾了吗」

> **称号与布局**：见 `2026-05-23-yinlema-titles-design.md`（本周称号为主指标；记录列表下划展示）。

**英雄区**

- 主文案：**已经 N 天没瘾了**（已由本周称号取代，见 titles spec）
- 次文案：**上次翻车至今 X 天 X 小时**
- 今日：**今天手滑 k 回了** / **今天还没瘾**

**主 CTA**

- **又瘾了** → `POST /records`，默认 `timestamp = now`
- 展开：**补记时间**（日期 + 时间），V1 无诱因表单

**列表**

- 按日分组，组内时间倒序；可删除单条；`note` 可选。

**图表**

- 天 / 周 / 月切换；柱 = 当日次数；折线 = 累计或 7 日滑动均值（与现版一致）。

### 3.3 今日检定 & 人设

- 标题倾向：**今日手气检定**、**瘾运 xx%**。
- 人设示例：戒断菩萨（假的）、深夜 emo 选手、表面清纯等。
- 不写库、不影响 streak。
- **扩展（9 人设 + 心河动画）**：见 `docs/superpowers/specs/2026-05-23-yinlema-identity-design.md`。

### 3.4 文案原则

1. **不羞耻**：不用脏 / 不洁 / 破戒 / 干净日。
2. **偏色轻松**：内部梗、双关（手滑、翻车、出动率等）。
3. **代码英文中性**：UI 才用梗。

---

## 4. 视觉与配色（女性向）

### 4.1 气质

- 柔和、偏暖、略带性感趣味（非严肃医疗、非男性向冷绿蓝）。
- 圆角、轻阴影、可选弱渐变英雄区。
- 图标与插画倾向：曲线、花瓣/云朵/丝带等抽象装饰（V1 可用 CSS 渐变代替插画）。

### 4.2 建议 CSS 变量（替换现 `global.css` 冷色）

```css
:root {
  color-scheme: light;
  --bg: #fdf2f8;              /* 浅玫瑰底 */
  --bg-elevated: #fce7f3;
  --card: #fffbff;
  --card-border: rgba(190, 24, 93, 0.08);
  --text: #4a044e;             /* 深梅紫字 */
  --muted: #9d174d;
  --accent-a: #ec4899;         /* 玫瑰主色 */
  --accent-b: #c084fc;         /* 薰衣草副色 */
  --accent-warm: #fb7185;      /* 珊瑚强调 */
  --danger: #e11d48;
  --radius-lg: 18px;
  --radius-md: 12px;
}
```

- 主按钮：玫瑰渐变 `linear-gradient(135deg, var(--accent-a), var(--accent-warm))`。
- 底部导航激活态：`accent-a`；未激活：`muted`。
- 图表系列色：玫瑰 / 薰衣草 / 浅珊瑚，不用 `#16a34a` 绿色主色。

### 4.3 组件微调

- `AppTopBar`、卡片、底部导航：统一暖粉阴影 `rgba(236, 72, 153, 0.12)`。
- 社交、排行图表 ECharts 主题色与 CSS 变量对齐。

---

## 5. 数据模型与 API

### 5.1 Record

```text
Record {
  _id
  user_id: string
  habit_type: "self_care_female"   # V1 默认
  timestamp: datetime
  date: "YYYY-MM-DD"               # 上海日历，冗余
  note: string = ""
  metadata: object = {}            # V1 恒为 {}
  created_at: datetime
}
```

### 5.2 API 变更摘要

| 方法 | 路径 | 变更 |
|------|------|------|
| GET/POST/DELETE | `/api/v1/records` | body/query 含 `habit_type`（默认 `self_care_female`） |
| GET | `/api/v1/records/stats` | 增加 `streak_days_no_record`, `since_last_ms`, `today_count`, `longest_streak_no_record` |
| GET | `/api/v1/rankings` | `metric=rate|count` 语义改为出动率 / 瘾次；数据源改 records |
| POST | `/api/v1/check-ins` | **V1 对前端移除**；后端可保留只读或 deprecated |

### 5.3 check_ins 迁移

1. 脚本：对每个 `check_ins.status == "deer"` 且当日无 record 的，插入一条等价 `records`（`habit_type=self_care_female`，时间取当日 12:00 上海时区或 `created_at`）。
2. 排行 / 小队服务改为只读 `records` 聚合。
3. 迁移验证后，`check_ins` 集合标记 deprecated（实现计划写明是否删除集合）。

### 5.4 用户（可选 V1）

- `users.default_habit_type = "self_care_female"`

---

## 6. 工程改名清单

| 层级 | 现值 | 新值 |
|------|------|------|
| 仓库 / 目录 | `lulemo` | `yinlema` |
| MongoDB | `lulemo` | `yinlema` |
| Docker | `lulemo-*` | `yinlema-*` |
| `APP_NAME` | 鹿了么 API | 瘾了吗 API |
| 前端 package | `lulemo-web` | `yinlema-web` |
| 生产 API 前缀 | `/lulemo-api/` | `/yinlema-api/` |
| 代码枚举 | `deer`, `CheckInStatus` | `habit_type`, `event_*`；`deer_male` 仅预留给鹿了吗模块 |

**命名约定**

- 用户可见：瘾了吗、又瘾了、没瘾了、出动率、瘾次。
- 代码：禁止在女性模块 UI 使用 `clean` / `dirty` / 鹿。

---

## 7. 后期路线图（不在 V1 实现）

| 阶段 | 内容 |
|------|------|
| V1.1 | 设置：每周最多 N 次（周目标达标展示） |
| V2 | `metadata`：诱因、地点；记录表单可选字段 |
| V2 | 习惯切换 UI；`deer_male` 鹿了吗子品牌；社交分榜 |
| V3 | 戒烟、戒手机等 `habit_type` |

---

## 8. 错误处理与边界

| 场景 | 行为 |
|------|------|
| 补记未来时间 | 400，提示「时间不能在未来」 |
| 删除不存在的 record | 404 |
| 无记录时 streak | `streak_days_no_record` = 自注册日或首条逻辑前的全部天数（与现 stats 一致，实现时复用 `dates_cn`） |
| 排行空数据 | 返回空列表，不报错 |
| 迁移重复执行 | 脚本幂等：按 `user_id + local_date` 去重 |

---

## 9. 测试范围（V1）

- 单元：streak / since_last / 出动率聚合（含同日多条、跨日、补记）。
- API：`POST /records` 默认 habit_type；stats 新字段；排行与 records 一致。
- 迁移脚本：check_in → record 对齐抽样验证。
- 前端：主屏文案、又瘾了流程、女性配色变量生效；社交页指标 label。
- 冒烟：注册 → 记 2 次同日 → streak 变 0 → 次日 streak +1。

---

## 10. 实施分期建议

1. **Phase A**：数据层（`habit_type`、stats、排行聚合、迁移脚本）。
2. **Phase B**：后端改名与路由文案；废弃 check-in 写接口。
3. **Phase C**：前端 rebranding（文案、导航、主屏、配色）。
4. **Phase D**：仓库/ Docker / 文档 / 环境变量 rename `yinlema`。
5. **Phase E**：鹿了吗相关代码仅留枚举与文档，不开发 UI。

---

## 附录：已确认的 brainstorming 决策

- 核心场景：女性自慰频率管理；按次记录；内部使用。
- 架构：方案一（records 唯一真相）+ `habit_type` 预埋。
- 统计 UI：已经 N 天没瘾了 + 上次翻车至今；后期周目标可配置。
- 社交：保留；出动率 / 瘾次。
- 气质：轻松偏色，不羞耻；主体配色女性向（玫瑰 / 薰衣草）。
- 平台名：瘾了吗；仓库名：yinlema；后期并入鹿了吗。
