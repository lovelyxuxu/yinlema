<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useIdentity } from "../stores/identity";
import { useRecords } from "../stores/records";

type Verdict = "none" | "lu" | "not";

const { activeRole } = useIdentity();
const { addRecord } = useRecords();

const verdict = ref<Verdict>("none");
const busy = ref(false);
const followMessage = ref("");
const synced = ref(false);

const LS_VERDICT = "lulemo:today:verdict";

onMounted(() => {
  const v = localStorage.getItem(LS_VERDICT);
  if (v === "lu" || v === "not") {
    verdict.value = v;
    followMessage.value = pickFollow(v);
    synced.value = true;
  }
});

watch(verdict, (v) => {
  if (v === "none") localStorage.removeItem(LS_VERDICT);
  else localStorage.setItem(LS_VERDICT, v);
});

const verdictConfig = computed(() => {
  if (verdict.value === "lu") {
    return {
      label: "鹿",
      icon: "🦌",
      color: "var(--danger)",
      glow: "rgba(248, 113, 113, 0.25)",
      gradFrom: "#f87171",
      gradTo: "#fb923c",
    };
  }
  if (verdict.value === "not") {
    return {
      label: "不鹿",
      icon: "🔱",
      color: "var(--accent-a)",
      glow: "rgba(34, 197, 94, 0.25)",
      gradFrom: "#22c55e",
      gradTo: "#38bdf8",
    };
  }
  return {
    label: "?",
    icon: "🎲",
    color: "var(--muted)",
    glow: "transparent",
    gradFrom: "#475569",
    gradTo: "#334155",
  };
});

const verdictHint = computed(() => {
  if (verdict.value === "none") return "按下按钮，让命运替你做决定。";
  return "想再来一次？随时可重新抽取。";
});

function pickFollow(v: Exclude<Verdict, "none">): string {
  const luPool = [
    "记得温柔对待自己：适度、放松、注意卫生与休息。",
    "今天把节奏放慢一点，给身体一点恢复时间。",
    "把它当作释放压力的一种方式，但别让它变成负担。",
    "享受当下，之后记得多喝水、好好休息。",
  ];
  const notPool = [
    "把精力留给运动、睡眠或一件小事的完成感。",
    "给身体一个缓冲日，明天再决定也不迟。",
    "试试转移注意力：散步、音乐、整理房间都很加分。",
    "今天积攒的能量，留着做些更有意义的事吧。",
  ];
  const pool = v === "lu" ? luPool : notPool;
  return pool[Math.floor(Math.random() * pool.length)]!;
}

function roll() {
  if (busy.value) return;
  busy.value = true;
  synced.value = false;
  const p = activeRole.value.luProbability;
  window.setTimeout(() => {
    const next: Exclude<Verdict, "none"> = Math.random() < p ? "lu" : "not";
    verdict.value = next;
    followMessage.value = pickFollow(next);
    busy.value = false;
  }, 600);
}

function syncToRecord() {
  if (verdict.value !== "lu" || synced.value) return;
  addRecord();
  synced.value = true;
}

function clearVerdict() {
  verdict.value = "none";
  followMessage.value = "";
  synced.value = false;
}
</script>

<template>
  <div class="page">
    <div class="card">
      <!-- 顶部 badge -->
      <div class="badge">
        <span class="dot" aria-hidden="true" />
        <span>随机决定今天鹿不鹿</span>
      </div>
      <h1 class="title">今日鹿么</h1>
      <p class="desc">
        当前身份：<strong>{{ activeRole.label }} {{ activeRole.emoji }}</strong>，
        鹿的概率约为 <strong>{{ Math.round(activeRole.luProbability * 100) }}%</strong>。
      </p>

      <!-- 结果展示区 -->
      <section
        class="panel"
        :class="{ 'panel-lu': verdict === 'lu', 'panel-not': verdict === 'not' }"
        aria-live="polite"
        :style="{ '--glow': verdictConfig.glow }"
      >
        <div class="panel-icon" :class="{ 'pop': !busy && verdict !== 'none' }">
          {{ verdictConfig.icon }}
        </div>
        <p class="panel-kicker">today's verdict</p>
        <p
          class="panel-title"
          :style="{ color: verdictConfig.color }"
          :class="{ 'reveal': !busy && verdict !== 'none' }"
        >
          {{ verdictConfig.label }}
        </p>
        <p class="panel-sub">{{ verdictHint }}</p>
        <transition name="fade-up">
          <p v-if="verdict !== 'none'" class="follow">{{ followMessage }}</p>
        </transition>

        <!-- 如果结果是「鹿」，提供同步到记录的按钮 -->
        <transition name="fade-up">
          <div v-if="verdict === 'lu'" class="sync-row">
            <button
              v-if="!synced"
              type="button"
              class="sync-btn"
              @click="syncToRecord"
            >
              记录到鹿了么
            </button>
            <span v-else class="synced-label">✓ 已记录到鹿了么</span>
          </div>
        </transition>
      </section>

      <!-- 操作按钮 -->
      <div class="actions">
        <button
          type="button"
          class="btn primary"
          :disabled="busy"
          @click="roll"
        >
          <span v-if="busy" class="spinner" aria-hidden="true" />
          {{ busy ? "命运转动中…" : verdict === "none" ? "开始今日鹿么" : "重新抽取" }}
        </button>
        <button
          v-if="verdict !== 'none'"
          type="button"
          class="btn ghost"
          :disabled="busy"
          @click="clearVerdict"
        >
          清空
        </button>
      </div>

      <p class="footer-note">结果按身份概率随机抽取，仅供娱乐与自我参考。</p>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 16px 14px 100px;
  display: flex;
  justify-content: center;
}

.card {
  width: min(560px, 100%);
  border-radius: 22px;
  padding: 18px 16px 16px;
  background: linear-gradient(180deg, rgba(20, 28, 40, 0.95), rgba(12, 16, 24, 0.95));
  border: 1px solid var(--card-border);
  box-shadow:
    0 18px 50px rgba(0, 0, 0, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: var(--muted);
  font-size: 12px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #e0f2fe, #38bdf8);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.55);
}

.title {
  margin: 12px 0 6px;
  font-size: 28px;
  line-height: 1.15;
  letter-spacing: 0.02em;
}

.desc {
  margin: 0 0 14px;
  color: rgba(226, 232, 240, 0.86);
  line-height: 1.65;
  font-size: 14px;
}

.desc strong {
  color: var(--text);
  font-weight: 700;
}

/* ── Panel ── */
.panel {
  margin-top: 4px;
  padding: 18px 16px;
  border-radius: var(--radius-lg);
  background: rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
  text-align: center;
}

.panel-lu {
  border-color: rgba(248, 113, 113, 0.3);
  background: rgba(248, 113, 113, 0.06);
  box-shadow: 0 0 40px var(--glow);
}

.panel-not {
  border-color: rgba(34, 197, 94, 0.3);
  background: rgba(34, 197, 94, 0.06);
  box-shadow: 0 0 40px var(--glow);
}

.panel-icon {
  font-size: 48px;
  line-height: 1;
  margin-bottom: 8px;
  display: block;
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.panel-icon.pop {
  animation: pop-in 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes pop-in {
  0%   { transform: scale(0.5) rotate(-10deg); opacity: 0; }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

.panel-kicker {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.8);
}

.panel-title {
  margin: 8px 0 4px;
  font-size: 42px;
  font-weight: 900;
  letter-spacing: 0.04em;
  transition: color 0.3s;
}

.panel-title.reveal {
  animation: reveal 0.4s ease forwards;
}

@keyframes reveal {
  0%   { opacity: 0; transform: translateY(12px) scale(0.9); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

.panel-sub {
  margin: 0 0 4px;
  color: rgba(226, 232, 240, 0.7);
  font-size: 13px;
}

.follow {
  margin: 12px 0 0;
  padding-top: 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
  color: rgba(224, 242, 254, 0.9);
  line-height: 1.65;
  font-size: 13px;
  text-align: left;
}

.sync-row {
  margin-top: 12px;
  text-align: center;
}

.sync-btn {
  background: rgba(248, 113, 113, 0.12);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #fca5a5;
  border-radius: 10px;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 600;
  transition: background 0.15s, transform 0.1s;
}

.sync-btn:hover {
  background: rgba(248, 113, 113, 0.2);
}

.sync-btn:active {
  transform: scale(0.96);
}

.synced-label {
  font-size: 13px;
  color: var(--accent-a);
}

/* ── Actions ── */
.actions {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

.btn {
  width: 100%;
  border-radius: 14px;
  padding: 14px;
  border: 1px solid transparent;
  font-weight: 800;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s, transform 0.1s;
}

.btn:active:not(:disabled) {
  transform: scale(0.98);
}

.btn.primary {
  color: #04120a;
  border: 0;
  background: linear-gradient(90deg, #22c55e, #38bdf8);
  box-shadow: 0 10px 28px rgba(34, 197, 94, 0.2);
}

.btn.primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.btn.ghost {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--muted);
}

/* Loading spinner */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(4, 18, 10, 0.3);
  border-top-color: rgba(4, 18, 10, 0.9);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.footer-note {
  margin: 12px 0 0;
  color: rgba(148, 163, 184, 0.7);
  font-size: 11px;
  line-height: 1.55;
  text-align: center;
}

/* Transition */
.fade-up-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
</style>
