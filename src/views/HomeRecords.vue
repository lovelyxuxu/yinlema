<script setup lang="ts">
import { computed, ref } from "vue";
import { useRecords, countByDay, countByWeek, countByMonth } from "../stores/records";

const { records, addRecord, removeRecord, streakDays, todayCount, recentFrequency } = useRecords();

type Tab = "day" | "week" | "month";
const activeTab = ref<Tab>("day");

const justRecorded = ref(false);

function handleAddRecord() {
  addRecord();
  justRecorded.value = true;
  setTimeout(() => (justRecorded.value = false), 2000);
}

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

const chartData = computed(() => {
  if (activeTab.value === "day") {
    const data = countByDay(7);
    const max = Math.max(...data.map((d) => d.count), 1);
    return data.map((d) => ({
      label: d.date.slice(5).replace("-", "/"),
      count: d.count,
      pct: d.count / max,
    }));
  }
  if (activeTab.value === "week") {
    const data = countByWeek(6);
    const max = Math.max(...data.map((d) => d.count), 1);
    return data.map((d) => ({
      label: d.label,
      count: d.count,
      pct: d.count / max,
    }));
  }
  const data = countByMonth(6);
  const max = Math.max(...data.map((d) => d.count), 1);
  return data.map((d) => ({
    label: d.label,
    count: d.count,
    pct: d.count / max,
  }));
});

const recentRecords = computed(() => records.value.slice(0, 10));

function formatTime(ts: number): string {
  const d = new Date(ts);
  const mo = String(d.getMonth() + 1).padStart(2, "0");
  const da = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${mo}-${da} ${hh}:${mm}`;
}
</script>

<template>
  <div class="page">

    <!-- 顶部 streak 横幅 -->
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
          @click="handleAddRecord"
        >
          {{ justRecorded ? "✓ 已记录" : "今天鹿了" }}
        </button>
      </div>
    </div>

    <!-- 统计图表 -->
    <div class="chart-card">
      <div class="chart-tabs">
        <button
          v-for="tab in [{ id: 'day', label: '按天' }, { id: 'week', label: '按周' }, { id: 'month', label: '按月' }]"
          :key="tab.id"
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id as Tab"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="chart">
        <div
          v-for="(item, i) in chartData"
          :key="i"
          class="chart-col"
        >
          <span class="bar-count">{{ item.count || "" }}</span>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ height: item.pct > 0 ? `${Math.max(item.pct * 100, 6)}%` : '0%' }"
            />
          </div>
          <span class="bar-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- 近期记录列表 -->
    <div class="record-list-card">
      <p class="card-eyebrow">近期记录</p>
      <div v-if="recentRecords.length === 0" class="empty-hint">
        还没有任何记录，点击「今天鹿了」开始记录。
      </div>
      <ul v-else class="record-list">
        <li
          v-for="rec in recentRecords"
          :key="rec.id"
          class="record-item"
        >
          <span class="record-dot" />
          <span class="record-time">{{ formatTime(rec.timestamp) }}</span>
          <button type="button" class="del-btn" @click="removeRecord(rec.id)" aria-label="删除">✕</button>
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

/* ── Streak Banner ── */
.streak-banner {
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(17, 24, 34, 0.95), rgba(10, 14, 22, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.07);
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

.streak-inner {
  display: flex;
  align-items: center;
  gap: 18px;
}

.streak-days {
  font-size: 64px;
  font-weight: 900;
  line-height: 1;
  color: var(--accent-color, var(--accent-b));
  text-shadow: 0 0 40px color-mix(in srgb, var(--accent-color, var(--accent-b)) 40%, transparent);
  min-width: 72px;
  text-align: center;
}

.streak-text {
  flex: 1;
}

.streak-title {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 700;
}

.streak-sub {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}

.streak-label {
  margin-top: 10px;
  font-size: 11px;
  color: rgba(148, 163, 184, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

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

.recommend-label {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
  color: var(--accent-a);
}

.recommend-hint {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.today-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 90px;
  gap: 2px;
}

.today-count {
  margin: 0;
  font-size: 40px;
  font-weight: 900;
  color: var(--accent-b);
  line-height: 1;
}

.today-unit {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--muted);
}

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

.record-btn.recorded {
  background: rgba(34, 197, 94, 0.18);
  color: var(--accent-a);
}

.record-btn:active {
  transform: scale(0.96);
}

/* ── Chart ── */
.chart-card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 14px;
}

.chart-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 14px;
}

.tab-btn {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid var(--card-border);
  background: transparent;
  color: var(--muted);
  transition: all 0.15s;
}

.tab-btn.active {
  background: rgba(56, 189, 248, 0.14);
  border-color: rgba(56, 189, 248, 0.4);
  color: var(--text);
}

.chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 100px;
}

.chart-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
}

.bar-count {
  font-size: 11px;
  color: var(--muted);
  height: 14px;
  line-height: 14px;
}

.bar-track {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 6px 6px 4px 4px;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  border-radius: 5px 5px 3px 3px;
  background: linear-gradient(180deg, var(--accent-b), rgba(56, 189, 248, 0.4));
  transition: height 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  min-height: 0;
}

.bar-label {
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
}

/* ── Record List ── */
.record-list-card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 14px;
}

.empty-hint {
  color: var(--muted);
  font-size: 13px;
  text-align: center;
  padding: 16px 0;
}

.record-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 6px;
  border-radius: var(--radius-md);
  transition: background 0.15s;
}

.record-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.record-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-b);
  opacity: 0.7;
  flex-shrink: 0;
}

.record-time {
  flex: 1;
  font-size: 14px;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}

.del-btn {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 12px;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
  opacity: 0.5;
}

.del-btn:hover {
  opacity: 1;
  color: var(--danger);
  background: rgba(248, 113, 113, 0.1);
}
</style>
