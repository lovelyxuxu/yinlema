<script setup lang="ts">
import { onMounted, ref } from "vue";
import { apiFetch, ApiError } from "../../api/client";

interface TeamCard {
  team_id: string;
  name: string;
  owner_user_id: string;
  auto_kick_miss_gt: number;
  member_count: number;
  created_at: string;
}

interface Member {
  user_id: string;
  joined_local_date: string;
}

interface Detail {
  team: TeamCard;
  members: Member[];
}

interface Stat {
  team_id: string;
  period: string;
  anchor: string;
  range_start: string;
  range_end: string;
  record_count: number;
  deer_rate: number;
}

const mine = ref<Detail | null>(null);
const loading = ref(false);
const err = ref("");

const createName = ref("");
const createKick = ref(20);

const joinId = ref("");

const statPeriod = ref<"day" | "week" | "month" | "year">("week");
const stat = ref<Stat | null>(null);

async function refresh() {
  loading.value = true;
  err.value = "";
  try {
    mine.value = await apiFetch<Detail | null>("/teams/mine");
    if (mine.value?.team.team_id) {
      await loadStat(mine.value.team.team_id);
    } else {
      stat.value = null;
    }
  } catch (e) {
    err.value = e instanceof ApiError ? e.detail : "加载失败";
  } finally {
    loading.value = false;
  }
}

async function loadStat(tid: string) {
  const q = new URLSearchParams({ period: statPeriod.value });
  stat.value = await apiFetch<Stat>(`/teams/${tid}/stats?${q.toString()}`);
}

onMounted(() => {
  refresh();
});

async function createTeam() {
  const n = createName.value.trim();
  if (!n) return;
  await apiFetch("/teams", {
    method: "POST",
    body: { name: n, auto_kick_miss_gt: createKick.value },
  });
  createName.value = "";
  await refresh();
}

async function joinTeam() {
  const id = joinId.value.trim();
  if (!id) return;
  await apiFetch(`/teams/${id}/join`, { method: "POST" });
  joinId.value = "";
  await refresh();
}

async function leaveTeam() {
  const tid = mine.value?.team.team_id;
  if (!tid) return;
  await apiFetch(`/teams/${tid}/leave`, { method: "POST" });
  await refresh();
}

async function changePeriod() {
  const tid = mine.value?.team.team_id;
  if (!tid) return;
  await loadStat(tid);
}
</script>

<template>
  <div class="teams">
    <p v-if="err" class="err">{{ err }}</p>
    <p v-if="loading" class="muted">载入中…</p>

    <section v-if="mine" class="card">
      <h2 class="title">我的小队 · {{ mine.team.name }}</h2>
      <p class="muted">成员 {{ mine.team.member_count }} · 缺席阈值（自然月天数 &gt; 该值将自动移出）</p>
      <p class="kb">
        Kick 规则：<strong>{{ mine.team.auto_kick_miss_gt }}</strong>
      </p>
      <p class="mono">小队 ID：<span>{{ mine.team.team_id }}</span></p>

      <div class="row">
        <button type="button" class="btn danger" @click="leaveTeam">退出小队</button>
      </div>

      <h3 class="sub">队内数据 · {{ statPeriod }}</h3>
      <select v-model="statPeriod" class="sel" autocomplete="off" @change="changePeriod">
        <option value="day">日</option>
        <option value="week">周</option>
        <option value="month">月</option>
        <option value="year">年</option>
      </select>
      <div v-if="stat" class="stat-grid">
        <div>
          <p class="label">区间内鹿次数（全员 records）</p>
          <p class="num">{{ stat.record_count }}</p>
        </div>
        <div>
          <p class="label">鹿率（Σ鹿了打卡天数 / Σ有打卡天数）</p>
          <p class="num">{{ (stat.deer_rate * 100).toFixed(2) }}%</p>
        </div>
        <div class="full">
          <p class="label">区间</p>
          <p class="mono small">{{ stat.range_start }} ~ {{ stat.range_end }}</p>
        </div>
      </div>

      <h3 class="sub">成员</h3>
      <ul class="mem">
        <li v-for="m in mine.members" :key="m.user_id" class="mono small">
          {{ m.user_id.slice(-6) }} · 加入日 {{ m.joined_local_date }}
        </li>
      </ul>
    </section>

    <section v-else-if="!loading" class="card">
      <h2 class="title">创建或加入</h2>
      <p class="muted">同一时间只能加入一个小队。小队榜仅统计 ≥10 人的队伍。</p>

      <div class="block">
        <p class="eyebrow">创建</p>
        <input
          v-model="createName"
          class="input"
          maxlength="32"
          placeholder="小队名称"
          autocomplete="off"
        />
        <label class="inline">
          自然月缺卡天数超过
          <input
            v-model.number="createKick"
            class="mini"
            type="number"
            min="0"
            max="31"
            autocomplete="off"
          />
          <span style="margin-left: 8px;">天自动踢出</span>
        </label>
        <button type="button" class="btn primary" @click="createTeam">创建小队</button>
      </div>

      <div class="block">
        <p class="eyebrow">加入（粘贴小队 ObjectId）</p>
        <input
          v-model="joinId"
          class="input mono"
          placeholder="例如 683a..."
          autocomplete="off"
        />
        <button type="button" class="btn" @click="joinTeam">加入</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.teams {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 16px;
}
.title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 800;
}
.sub {
  margin: 16px 0 8px;
  font-size: 14px;
  font-weight: 700;
}
.muted {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
}
.err {
  color: var(--danger);
  font-size: 13px;
}
.kb strong {
  color: var(--accent-b);
}
.mono {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.mono.small {
  font-size: 11px;
}
.row {
  margin-top: 10px;
}
.btn {
  border-radius: 12px;
  border: 1px solid var(--card-border);
  padding: 10px 16px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.05);
  color: var(--text);
}
.btn.primary {
  border: none;
  background: var(--accent-a);
  color: #fff;
}
.btn.danger {
  border-color: rgba(239, 68, 68, 0.35);
  color: var(--danger);
}
.input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--card-border);
  background: rgba(0, 0, 0, 0.04);
  color: var(--text);
  margin-bottom: 8px;
}
.mini {
  width: 56px;
  margin-left: 8px;
  padding: 4px;
  border-radius: 8px;
  border: 1px solid var(--card-border);
  background: rgba(0, 0, 0, 0.04);
  color: var(--text);
}
.block {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--card-border);
}
.eyebrow {
  margin: 0 0 6px;
  font-size: 11px;
  color: var(--muted);
  font-weight: 700;
  letter-spacing: 0.08em;
}
.inline {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
}
.sel {
  border-radius: 10px;
  border: 1px solid var(--card-border);
  background: rgba(0, 0, 0, 0.04);
  color: var(--text);
  padding: 8px;
  margin-bottom: 10px;
}
.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.stat-grid .full {
  grid-column: 1 / -1;
}
.label {
  margin: 0;
  font-size: 11px;
  color: var(--muted);
}
.num {
  margin: 4px 0 0;
  font-size: 22px;
  font-weight: 900;
  color: var(--accent-b);
}
.mem {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
</style>
