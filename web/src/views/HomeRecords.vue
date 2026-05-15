<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRecords, countByDay, countByWeek, countByMonth, countByYear } from "../stores/records";
import { useAuth } from "../stores/auth";
import { useRouter } from "vue-router";

const {
  records, addRecord, removeRecord, updateNote,
  fetchRecords, loading, streakDays, todayCount, recentFrequency,
} = useRecords();
const { logout } = useAuth();
const router = useRouter();

/* ── Tab ── */
type Tab = "day" | "week" | "month" | "year";
const activeTab = ref<Tab>("day");

const chartTabs: { id: Tab; label: string }[] = [
  { id: "day", label: "按天" },
  { id: "week", label: "按周" },
  { id: "month", label: "按月" },
  { id: "year", label: "按年" },
];

function setChartTab(id: Tab) {
  activeTab.value = id;
}

/* ── 今日记录按钮 ── */
const justRecorded = ref(false);
const addingRecord = ref(false);

onMounted(() => { fetchRecords().catch(() => {}); });

async function handleAddRecord() {
  if (addingRecord.value) return;
  addingRecord.value = true;
  try {
    await addRecord();
    justRecorded.value = true;
    setTimeout(() => (justRecorded.value = false), 2000);
  } finally {
    addingRecord.value = false;
  }
}

function handleLogout() {
  logout();
  router.push("/auth");
}

/* ── 统计横幅 ── */
const streakBanner = computed(() => {
  const n = streakDays.value;
  if (n === 0) return { title: "今天已经鹿了", sub: "今天好好照顾一下自己，给身体留点时间恢复。", color: "var(--danger)" };
  if (n < 3)  return { title: `${n} 天没鹿`, sub: "好的开始！每一天都是一次选择，继续。", color: "var(--accent-b)" };
  if (n < 7)  return { title: `${n} 天没鹿`, sub: "已经坚持好几天了，精力是不是更充沛了？", color: "var(--accent-b)" };
  if (n < 14) return { title: `整整 ${n} 天！`, sub: "一周以上，节律在慢慢建立。你比昨天更强。", color: "var(--accent-a)" };
  if (n < 30) return { title: `${n} 天！真的厉害`, sub: "半个月了，这已经是一种习惯的力量了。", color: "var(--accent-a)" };
  return { title: `${n} 天！西格玛境界`, sub: "一个月以上，你已经踏入了真正自律的领域。🔱", color: "#a78bfa" };
});

const recommendation = computed(() => {
  const freq = recentFrequency.value;
  if (freq === 0) return { label: "完全休整", hint: "近一周没有记录，身体已在充分恢复中。" };
  if (freq < 0.3) return { label: "适度建议", hint: "近一周频率较低，状态不错，继续保持。" };
  if (freq < 0.6) return { label: "注意节律", hint: "近一周频率适中，今天可以考虑休息一下。" };
  return { label: "今日建议休息", hint: "近一周频率偏高，身体需要缓冲，今天放一放吧。" };
});

/* ── 图表（含 filterKey）── */
function ds(d: Date) { return d.toISOString().slice(0, 10); }

interface ChartBarItem {
  label: string;
  count: number;
  pct: number;
  filterKey: string;
}

/** 按天视图展示的日历天数（仅图表维度；左右滑动查看更早日期） */
const CHART_DAY_RANGE = 180;
/** 按年视图展示的年份个数（含本年） */
const CHART_YEAR_RANGE = 6;

const chartData = computed((): ChartBarItem[] => {
  if (activeTab.value === "day") {
    const n = CHART_DAY_RANGE;
    const raw = countByDay(n);
    const max = Math.max(...raw.map((d) => d.count), 1);
    const items = raw.map((d) => ({
      label: d.date.slice(5).replace("-", "/"),
      count: d.count,
      pct: d.count / max,
      filterKey: d.date,
    }));
    items.reverse(); // 新→旧（左：最近）
    return items;
  }
  if (activeTab.value === "week") {
    const n = 8;
    const raw = countByWeek(n);
    const max = Math.max(...raw.map((d) => d.count), 1);
    const items = raw.map((d, j) => {
      const i = n - 1 - j;
      const end = new Date(); end.setDate(end.getDate() - i * 7);
      const start = new Date(end); start.setDate(start.getDate() - 6);
      return { label: d.label, count: d.count, pct: d.count / max, filterKey: `${ds(start)}~${ds(end)}` };
    });
    items.reverse();
    return items;
  }
  if (activeTab.value === "month") {
    const n = 12;
    const raw = countByMonth(n);
    const max = Math.max(...raw.map((d) => d.count), 1);
    const now = new Date();
    const items = raw.map((d, j) => {
      const i = n - 1 - j;
      const md = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const prefix = `${md.getFullYear()}-${String(md.getMonth() + 1).padStart(2, "0")}`;
      return { label: d.label, count: d.count, pct: d.count / max, filterKey: prefix };
    });
    items.reverse();
    return items;
  }
  if (activeTab.value === "year") {
    const n = CHART_YEAR_RANGE;
    const raw = countByYear(n);
    const max = Math.max(...raw.map((d) => d.count), 1);
    const items = raw.map((d) => ({
      label: d.label,
      count: d.count,
      pct: d.count / max,
      filterKey: String(d.year),
    }));
    items.reverse();
    return items;
  }
  return [];
});

/* ── 图表选中 → 筛选记录 ── */
const selectedBarKey = ref<string | null>(null);
watch(activeTab, () => { selectedBarKey.value = null; });

function selectBar(key: string) {
  selectedBarKey.value = selectedBarKey.value === key ? null : key;
}

const filterLabel = computed(() => {
  const key = selectedBarKey.value;
  if (!key) return null;
  if (activeTab.value === "day") return key.slice(5).replace("-", "/");
  if (activeTab.value === "week") {
    const [s, e] = key.split("~");
    return `${s.slice(5).replace("-", "/")} - ${e.slice(5).replace("-", "/")}`;
  }
  if (activeTab.value === "month") return `${parseInt(key.slice(5), 10)}月`;
  if (activeTab.value === "year") return `${key}年`;
  return key;
});

const filteredRecords = computed(() => {
  const key = selectedBarKey.value;
  if (!key) return records.value.slice(0, 50);
  if (activeTab.value === "day") return records.value.filter((r) => r.date === key);
  if (activeTab.value === "week") {
    const [start, end] = key.split("~");
    return records.value.filter((r) => r.date >= start && r.date <= end);
  }
  if (activeTab.value === "month") return records.value.filter((r) => r.date.startsWith(key));
  if (activeTab.value === "year") return records.value.filter((r) => r.date.startsWith(`${key}-`));
  return [];
});

/* ── 记录展开 / 备注编辑 ── */
const expandedIds = reactive<string[]>([]);
const editingId = ref<string | null>(null);
const draftNote = ref("");
const savingNote = ref(false);

function isExpanded(id: string) { return expandedIds.includes(id); }

function toggleExpand(id: string) {
  const idx = expandedIds.indexOf(id);
  if (idx >= 0) {
    expandedIds.splice(idx, 1);
    if (editingId.value === id) { editingId.value = null; draftNote.value = ""; }
  } else {
    expandedIds.push(id);
  }
}

function startEdit(id: string, current: string) {
  editingId.value = id;
  draftNote.value = current;
}

function cancelEdit() {
  editingId.value = null;
  draftNote.value = "";
}

async function confirmNote(id: string) {
  if (savingNote.value) return;
  savingNote.value = true;
  try {
    await updateNote(id, draftNote.value.trim());
    editingId.value = null;
    draftNote.value = "";
  } finally {
    savingNote.value = false;
  }
}

async function handleRemoveRecord(id: string) {
  await removeRecord(id);
  const idx = expandedIds.indexOf(id);
  if (idx >= 0) expandedIds.splice(idx, 1);
  if (editingId.value === id) { editingId.value = null; draftNote.value = ""; }
}

function formatTime(ts: number): string {
  const d = new Date(ts);
  return `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
</script>

<template>
  <div class="page">

    <!-- 顶栏 -->
    <div class="topbar">
      <span class="topbar-title">鹿了么</span>
      <button type="button" class="logout-btn" @click="handleLogout">退出</button>
    </div>

    <!-- 加载占位 -->
    <div v-if="loading" class="loading-hint">
      <span class="loading-dot" /><span class="loading-dot" /><span class="loading-dot" />
    </div>

    <!-- Streak 横幅 -->
    <div class="streak-banner" :style="{ '--accent-color': streakBanner.color }">
      <div class="streak-inner">
        <div class="streak-days">{{ streakDays }}</div>
        <div class="streak-text">
          <p class="streak-title">{{ streakBanner.title }}</p>
          <p class="streak-sub">{{ streakBanner.sub }}</p>
        </div>
      </div>
      <div class="streak-label">连续天数</div>
    </div>

    <!-- 今日推荐 + 记录按钮 -->
    <div class="row-two">
      <div class="recommend-card">
        <p class="card-eyebrow">今日参考</p>
        <p class="recommend-label">{{ recommendation.label }}</p>
        <p class="recommend-hint">{{ recommendation.hint }}</p>
      </div>
      <div class="today-card">
        <p class="card-eyebrow">今日</p>
        <p class="today-count">{{ todayCount }}</p>
        <p class="today-unit">次</p>
        <button
          type="button"
          class="record-btn"
          :class="{ recorded: justRecorded }"
          :disabled="addingRecord"
          @click="handleAddRecord"
        >
          {{ justRecorded ? "✓ 已记录" : addingRecord ? "记录中…" : "今天鹿了" }}
        </button>
      </div>
    </div>

    <!-- 统计图表 -->
    <div class="chart-card">
      <div class="chart-tabs">
        <button
          v-for="tab in chartTabs"
          :key="tab.id"
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="setChartTab(tab.id)"
        >{{ tab.label }}</button>
      </div>

      <!-- 可横向滚动的图表区域 -->
      <div class="chart-scroll">
        <div class="chart">
          <div
            v-for="item in chartData"
            :key="`${activeTab}-${item.filterKey}`"
            class="chart-col"
            :class="{ selected: selectedBarKey === item.filterKey }"
            @click="selectBar(item.filterKey)"
          >
            <span class="bar-count">{{ item.count || "" }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ height: item.pct > 0 ? `${Math.max(item.pct * 100, 5)}%` : '0%' }"
              />
            </div>
            <span class="bar-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 记录列表 -->
    <div class="record-list-card">
      <div class="record-list-header">
        <p class="card-eyebrow">记录</p>
        <button v-if="selectedBarKey" type="button" class="filter-badge" @click="selectedBarKey = null">
          {{ filterLabel }} <span class="filter-close">×</span>
        </button>
      </div>

      <div v-if="filteredRecords.length === 0" class="empty-hint">
        {{ selectedBarKey ? "该时间段暂无记录" : "还没有任何记录，点击「今天鹿了」开始记录。" }}
      </div>

      <ul v-else class="record-list">
        <li
          v-for="rec in filteredRecords"
          :key="rec.id"
          class="record-item-wrapper"
        >
          <!-- 主行 -->
          <div class="record-row">
            <span class="record-dot" :class="{ 'has-note': !!rec.note }" />
            <span class="record-time">{{ formatTime(rec.timestamp) }}</span>
            <button
              type="button"
              class="expand-btn"
              :class="{ expanded: isExpanded(rec.id) }"
              :aria-label="isExpanded(rec.id) ? '收起' : '展开'"
              @click="toggleExpand(rec.id)"
            >
              <svg viewBox="0 0 12 12" fill="none" width="12" height="12">
                <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <!-- 展开详情 -->
          <transition name="detail-slide">
            <div v-if="isExpanded(rec.id)" class="record-detail">
              <!-- 编辑状态 -->
              <template v-if="editingId === rec.id">
                <textarea
                  v-model="draftNote"
                  class="note-input"
                  placeholder="写下这一刻的感受…"
                  rows="3"
                  :disabled="savingNote"
                />
                <div class="note-edit-actions">
                  <button type="button" class="cancel-btn" :disabled="savingNote" @click="cancelEdit">取消</button>
                  <button type="button" class="confirm-btn" :disabled="savingNote" @click="confirmNote(rec.id)">
                    {{ savingNote ? "保存中…" : "确认" }}
                  </button>
                </div>
              </template>

              <!-- 有备注 -->
              <template v-else-if="rec.note">
                <p class="note-text">{{ rec.note }}</p>
                <div class="detail-footer">
                  <button type="button" class="edit-note-btn" @click="startEdit(rec.id, rec.note)">编辑</button>
                  <button type="button" class="del-record-btn" @click="handleRemoveRecord(rec.id)">删除此条</button>
                </div>
              </template>

              <!-- 无备注 -->
              <template v-else>
                <div class="note-empty-row">
                  <button type="button" class="write-btn" @click="startEdit(rec.id, '')">写点啥</button>
                  <button type="button" class="del-record-btn" @click="handleRemoveRecord(rec.id)">删除此条</button>
                </div>
              </template>
            </div>
          </transition>
        </li>
      </ul>
    </div>

  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 16px 14px 100px;
  max-width: 560px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── Topbar ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 2px 4px;
}
.topbar-title {
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.04em;
  background: linear-gradient(90deg, var(--accent-a), var(--accent-b));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.logout-btn {
  background: none;
  border: 1px solid var(--card-border);
  color: var(--muted);
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 999px;
  transition: color 0.15s, border-color 0.15s;
}
.logout-btn:hover { color: var(--text); border-color: rgba(255,255,255,0.2); }

/* ── Loading ── */
.loading-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 20px 0 8px;
}
.loading-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-b);
  opacity: 0.7;
  animation: dot-bounce 1s ease-in-out infinite;
}
.loading-dot:nth-child(2) { animation-delay: 0.15s; }
.loading-dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes dot-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-8px); opacity: 1; }
}

/* ── Streak Banner ── */
.streak-banner {
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(17,24,34,0.95), rgba(10,14,22,0.95));
  border: 1px solid rgba(255,255,255,0.07);
  padding: 18px 18px 14px;
  position: relative;
  overflow: hidden;
}
.streak-banner::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(135deg, var(--accent-color, var(--accent-b)), transparent 60%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
.streak-inner { display: flex; align-items: center; gap: 18px; }
.streak-days {
  font-size: 64px;
  font-weight: 900;
  line-height: 1;
  color: var(--accent-color, var(--accent-b));
  text-shadow: 0 0 40px color-mix(in srgb, var(--accent-color, var(--accent-b)) 40%, transparent);
  min-width: 72px;
  text-align: center;
}
.streak-text { flex: 1; }
.streak-title { margin: 0 0 4px; font-size: 17px; font-weight: 700; }
.streak-sub { margin: 0; font-size: 13px; color: var(--muted); line-height: 1.55; }
.streak-label { margin-top: 10px; font-size: 11px; color: rgba(148,163,184,0.5); text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Two-column row ── */
.row-two {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: stretch;
}
.card-eyebrow {
  margin: 0 0 6px;
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.recommend-card,
.today-card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 14px;
}
.recommend-label { margin: 0 0 4px; font-size: 15px; font-weight: 700; color: var(--accent-a); }
.recommend-hint { margin: 0; font-size: 13px; color: var(--muted); line-height: 1.5; }
.today-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 90px;
  gap: 2px;
}
.today-count { margin: 0; font-size: 40px; font-weight: 900; color: var(--accent-b); line-height: 1; }
.today-unit { margin: 0 0 8px; font-size: 12px; color: var(--muted); }
.record-btn {
  width: 100%;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 13px;
  font-weight: 700;
  border: none;
  background: linear-gradient(90deg, var(--accent-a), var(--accent-b));
  color: #04120a;
  transition: opacity 0.2s, transform 0.1s;
}
.record-btn.recorded { background: rgba(34,197,94,0.18); color: var(--accent-a); }
.record-btn:active { transform: scale(0.96); }

/* ── Chart ── */
.chart-card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 14px;
}
.chart-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-bottom: 14px;
}
.tab-btn {
  padding: 6px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--card-border);
  background: transparent;
  color: var(--muted);
  transition: all 0.15s;
}
.tab-btn.active {
  background: rgba(56,189,248,0.14);
  border-color: rgba(56,189,248,0.4);
  color: var(--text);
}

/* 滚动容器 */
.chart-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 2px;
  /* 去掉移动端点击时出现的那段半透明浅色闪烁（浏览器自带 tap highlight） */
  -webkit-tap-highlight-color: transparent;
}
.chart-scroll::-webkit-scrollbar { display: none; }

.chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 160px;
  /* 保持每列最小宽度，超出父容器宽度时才滚动 */
  min-width: max-content;
  width: 100%;
}

.chart-col {
  min-width: 44px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  cursor: pointer;
  border-radius: var(--radius-md);
  padding: 4px 2px 2px;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  user-select: none;
}
.chart-col:hover { background: rgba(255,255,255,0.04); }
.chart-col.selected { background: rgba(56,189,248,0.1); }

.bar-count { font-size: 11px; color: var(--muted); height: 14px; line-height: 14px; }
.bar-track {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  background: rgba(255,255,255,0.04);
  border-radius: 6px 6px 4px 4px;
  overflow: hidden;
}
.bar-fill {
  width: 100%;
  border-radius: 5px 5px 3px 3px;
  background: linear-gradient(180deg, var(--accent-b), rgba(56,189,248,0.4));
  transition: height 0.4s cubic-bezier(0.34,1.56,0.64,1);
  min-height: 0;
}
.chart-col.selected .bar-fill {
  background: linear-gradient(180deg, #60e6ff, rgba(56,189,248,0.7));
}
.bar-label {
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
  max-width: 100%;
  text-align: center;
}
.chart-col.selected .bar-label { color: var(--accent-b); }

/* ── Record List ── */
.record-list-card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 14px;
}
.record-list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.record-list-header .card-eyebrow { margin-bottom: 0; }

.filter-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-b);
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.3);
  transition: background 0.15s;
}
.filter-badge:hover { background: rgba(56,189,248,0.18); }
.filter-close { opacity: 0.7; }

.empty-hint {
  color: var(--muted);
  font-size: 13px;
  text-align: center;
  padding: 16px 0;
}

.record-list {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* 记录条目 */
.record-item-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: background 0.15s;
}
.record-item-wrapper:hover { background: rgba(255,255,255,0.02); }

.record-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 6px;
}

.record-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-b);
  opacity: 0.6;
  flex-shrink: 0;
  transition: background 0.2s, opacity 0.2s;
}
.record-dot.has-note {
  background: var(--accent-a);
  opacity: 0.9;
}

.record-time {
  flex: 1;
  font-size: 14px;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}

.expand-btn {
  background: none;
  border: none;
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s, transform 0.25s ease;
}
.expand-btn:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.expand-btn.expanded { transform: rotate(180deg); color: var(--accent-b); }

/* 展开详情 */
.record-detail {
  padding: 0 8px 10px 23px;
}

.note-input {
  width: 100%;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  color: var(--text);
  font-size: 13px;
  padding: 10px 12px;
  resize: none;
  outline: none;
  line-height: 1.6;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.note-input:focus {
  border-color: rgba(56,189,248,0.45);
  box-shadow: 0 0 0 3px rgba(56,189,248,0.08);
}
.note-input:disabled { opacity: 0.5; }

.note-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
.cancel-btn {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: none;
  border: 1px solid var(--card-border);
  color: var(--muted);
}
.cancel-btn:hover { color: var(--text); }
.confirm-btn {
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(56,189,248,0.15);
  border: 1px solid rgba(56,189,248,0.35);
  color: var(--accent-b);
  transition: background 0.15s;
}
.confirm-btn:hover { background: rgba(56,189,248,0.25); }
.confirm-btn:disabled, .cancel-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.note-text {
  margin: 0 0 8px;
  font-size: 13px;
  color: rgba(226,232,240,0.85);
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-footer,
.note-empty-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.write-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  background: rgba(255,255,255,0.05);
  border: 1px dashed rgba(255,255,255,0.12);
  border-radius: 8px;
  padding: 5px 14px;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
.write-btn:hover { color: var(--text); border-color: rgba(255,255,255,0.22); background: rgba(255,255,255,0.08); }

.edit-note-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  background: none;
  border: none;
  padding: 4px 0;
  transition: color 0.15s;
}
.edit-note-btn:hover { color: var(--accent-b); }

.del-record-btn {
  font-size: 12px;
  font-weight: 600;
  color: rgba(248,113,113,0.5);
  background: none;
  border: none;
  padding: 4px 0;
  margin-left: auto;
  transition: color 0.15s;
}
.del-record-btn:hover { color: var(--danger); }

/* 展开动画 */
.detail-slide-enter-active {
  transition: max-height 0.28s ease, opacity 0.2s ease;
  max-height: 260px;
  overflow: hidden;
}
.detail-slide-leave-active {
  transition: max-height 0.22s ease, opacity 0.18s ease;
  max-height: 260px;
  overflow: hidden;
}
.detail-slide-enter-from,
.detail-slide-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
