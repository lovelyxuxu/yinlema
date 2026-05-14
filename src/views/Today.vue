<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useIdentity } from "../stores/identity";

type Verdict = "none" | "lu" | "not";

const { activeRole } = useIdentity();

const verdict = ref<Verdict>("none");
const busy = ref(false);
const followMessage = ref("");

const LS_VERDICT = "lulemo:today:verdict";

onMounted(() => {
  const v = localStorage.getItem(LS_VERDICT);
  if (v === "lu" || v === "not") {
    verdict.value = v;
    followMessage.value = pickFollow(v);
  }
});

watch(verdict, (v) => {
  if (v === "none") localStorage.removeItem(LS_VERDICT);
  else localStorage.setItem(LS_VERDICT, v);
});

const verdictLabel = computed(() => {
  if (verdict.value === "lu") return "鹿";
  if (verdict.value === "not") return "不鹿";
  return "未选择";
});

const verdictHint = computed(() => {
  if (verdict.value === "none") return "点击下方按钮开始抽取结果。";
  return "想再来一次？随时可重新抽取。";
});

function pickFollow(v: Exclude<Verdict, "none">): string {
  const luPool = [
    "记得温柔对待自己：适度、放松、注意卫生与休息。",
    "今天把节奏放慢一点，给身体一点恢复时间。",
    "把它当作释放压力的一种方式，但别让它变成负担。",
  ];
  const notPool = [
    "也不错：把精力留给运动、睡眠或一件小事的完成感。",
    "给身体一个缓冲日，明天再决定也不迟。",
    "试试转移注意力：散步、音乐、整理房间都很加分。",
  ];
  const pool = v === "lu" ? luPool : notPool;
  return pool[Math.floor(Math.random() * pool.length)]!;
}

function roll() {
  if (busy.value) return;
  busy.value = true;
  const p = activeRole.value.luProbability;
  window.setTimeout(() => {
    const next: Exclude<Verdict, "none"> = Math.random() < p ? "lu" : "not";
    verdict.value = next;
    followMessage.value = pickFollow(next);
    busy.value = false;
  }, 520);
}

function clearRecords() {
  verdict.value = "none";
  followMessage.value = "";
}
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="badge">
        <span class="dot" aria-hidden="true" />
        <span>随机决定今天鹿不鹿</span>
      </div>
      <h1 class="title">今天鹿不鹿</h1>
      <p class="desc">
        按一下按钮，让系统随机告诉你今天是“鹿”还是“不鹿”。可以当作心情开关、今日运势，或者纯粹图一乐。当前身份下「鹿」的概率约为
        <strong>{{ Math.round(activeRole.luProbability * 100) }}%</strong>。
      </p>

      <section class="panel" aria-live="polite">
        <p class="panel-kicker">today's verdict</p>
        <p class="panel-title">{{ verdictLabel }}</p>
        <p class="panel-sub">{{ verdictHint }}</p>
        <p v-if="verdict !== 'none'" class="follow">{{ followMessage }}</p>
      </section>

      <div class="actions">
        <button type="button" class="btn primary" :disabled="busy" @click="roll">
          {{ busy ? "请稍候…" : "开始今天鹿不鹿" }}
        </button>
        <button type="button" class="btn ghost" :disabled="busy" @click="clearRecords">
          清空记录
        </button>
      </div>

      <p class="footer-note">提示：结果完全随机，按身份设定的概率抽取，仅供娱乐与自我参考。</p>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 18px 14px 96px;
  display: flex;
  justify-content: center;
}

.card {
  width: min(560px, 100%);
  border-radius: 22px;
  padding: 18px 16px 16px;
  background: linear-gradient(180deg, rgba(20, 28, 40, 0.92), rgba(12, 16, 24, 0.92));
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
  margin: 12px 0 8px;
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
  color: #e0f2fe;
  font-weight: 800;
}

.panel {
  margin-top: 4px;
  padding: 14px 14px;
  border-radius: var(--radius-lg);
  background: rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-kicker {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.95);
}

.panel-title {
  margin: 10px 0 6px;
  font-size: 26px;
  font-weight: 800;
}

.panel-sub {
  margin: 0;
  color: rgba(226, 232, 240, 0.86);
  line-height: 1.55;
  font-size: 14px;
}

.follow {
  margin: 12px 0 0;
  padding-top: 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.12);
  color: rgba(224, 242, 254, 0.92);
  line-height: 1.6;
}

.actions {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

.btn {
  width: 100%;
  border-radius: 14px;
  padding: 14px 14px;
  border: 1px solid transparent;
  font-weight: 800;
}

.btn.primary {
  color: #04120a;
  border: 0;
  background: linear-gradient(90deg, #22c55e, #38bdf8);
  box-shadow: 0 14px 30px rgba(34, 197, 94, 0.18);
}

.btn.primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.btn.ghost {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.12);
  color: var(--text);
}

.footer-note {
  margin: 12px 0 0;
  color: rgba(148, 163, 184, 0.95);
  font-size: 12px;
  line-height: 1.55;
}
</style>
