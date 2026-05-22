<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { apiFetch, ApiError } from "../../api/client";
import MobileSelect from "../../components/MobileSelect.vue";

/* ─── 类型 ─────────────────────────────────────────────── */
interface TeamCard {
  team_id: string;
  name: string;
  owner_user_id: string;
  auto_kick_miss_gt: number;
  member_count: number;
  created_at: string;
  is_mine: boolean;
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
  range_start: string;
  range_end: string;
  record_count: number;
  deer_rate: number;
}

/* ─── 共享状态 ──────────────────────────────────────────── */
const tab = ref<"mine" | "plaza">("mine");
const myDetail = ref<Detail | null>(null);
const myLoading = ref(false);
const myErr = ref("");

/* ─── 我的小组 ──────────────────────────────────────────── */
const statPeriodOptions = [
  { value: "day", label: "日" },
  { value: "week", label: "周" },
  { value: "month", label: "月" },
  { value: "year", label: "年" },
];
const statPeriod = ref<"day" | "week" | "month" | "year">("week");
const stat = ref<Stat | null>(null);

async function loadMine() {
  myLoading.value = true;
  myErr.value = "";
  try {
    myDetail.value = await apiFetch<Detail | null>("/teams/mine");
    if (myDetail.value?.team.team_id) {
      await loadStat(myDetail.value.team.team_id);
    } else {
      stat.value = null;
    }
  } catch (e) {
    myErr.value = e instanceof ApiError ? e.detail : "加载失败";
  } finally {
    myLoading.value = false;
  }
}

async function loadStat(tid: string) {
  const q = new URLSearchParams({ period: statPeriod.value });
  stat.value = await apiFetch<Stat>(`/teams/${tid}/stats?${q.toString()}`);
}

watch(statPeriod, () => {
  const tid = myDetail.value?.team.team_id;
  if (tid) loadStat(tid);
});

async function leaveTeam() {
  const tid = myDetail.value?.team.team_id;
  if (!tid) return;
  try {
    await apiFetch(`/teams/${tid}/leave`, { method: "POST" });
    await loadMine();
    await loadPlaza();
  } catch (e) {
    myErr.value = e instanceof ApiError ? e.detail : "退出失败";
  }
}

/* ─── 创建小组弹层 ──────────────────────────────────────── */
const showCreate = ref(false);
const createName = ref("");
const createKick = ref(20);
const createSubmitting = ref(false);
const createErr = ref("");
const createNameRef = ref<HTMLInputElement | null>(null);

function openCreate() {
  createName.value = "";
  createKick.value = 20;
  createErr.value = "";
  showCreate.value = true;
  nextTick(() => createNameRef.value?.focus());
}
function closeCreate() { showCreate.value = false; }

async function submitCreate() {
  const n = createName.value.trim();
  if (!n || createSubmitting.value) return;
  createSubmitting.value = true;
  createErr.value = "";
  try {
    await apiFetch("/teams", {
      method: "POST",
      body: { name: n, auto_kick_miss_gt: createKick.value },
    });
    closeCreate();
    await loadMine();
    await loadPlaza();
  } catch (e) {
    createErr.value = e instanceof ApiError ? e.detail : "创建失败";
  } finally {
    createSubmitting.value = false;
  }
}

/* ─── 小组广场 ──────────────────────────────────────────── */
const plazaList = ref<TeamCard[]>([]);
const plazaLoading = ref(false);
const plazaErr = ref("");
const searchQ = ref("");
let searchTimer: ReturnType<typeof setTimeout> | null = null;

const isInAnyTeam = computed(() => !!myDetail.value);

async function loadPlaza(q = searchQ.value) {
  plazaLoading.value = true;
  plazaErr.value = "";
  try {
    const params = new URLSearchParams();
    if (q.trim()) params.set("q", q.trim());
    plazaList.value = await apiFetch<TeamCard[]>(`/teams?${params.toString()}`);
  } catch (e) {
    plazaErr.value = e instanceof ApiError ? e.detail : "加载失败";
  } finally {
    plazaLoading.value = false;
  }
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadPlaza(), 320);
}

/* ─── 申请加入 ──────────────────────────────────────────── */
const joiningId = ref<string | null>(null);
const joinErrMap = ref<Record<string, string>>({});

async function joinTeam(tid: string) {
  if (joiningId.value) return;
  joiningId.value = tid;
  delete joinErrMap.value[tid];
  try {
    await apiFetch(`/teams/${tid}/join`, { method: "POST" });
    await loadMine();
    await loadPlaza();
  } catch (e) {
    joinErrMap.value[tid] = e instanceof ApiError ? e.detail : "加入失败";
  } finally {
    joiningId.value = null;
  }
}

/* ─── 切换 tab 时按需加载 ───────────────────────────────── */
watch(tab, (v) => {
  if (v === "plaza" && plazaList.value.length === 0) loadPlaza();
});

onMounted(() => {
  loadMine();
});
</script>

<template>
  <div class="teams">
    <!-- 内部 tab 切换 -->
    <div class="tab-bar">
      <button
        type="button"
        class="tab-pill"
        :class="{ active: tab === 'mine' }"
        @click="tab = 'mine'"
      >
        我的小组
      </button>
      <button
        type="button"
        class="tab-pill"
        :class="{ active: tab === 'plaza' }"
        @click="tab = 'plaza'"
      >
        小组广场
      </button>
    </div>

    <!-- ══════════ 我的小组 ══════════ -->
    <template v-if="tab === 'mine'">
      <p v-if="myErr" class="err">{{ myErr }}</p>
      <p v-if="myLoading && !myDetail" class="muted center">载入中…</p>

      <!-- 已加入小组 -->
      <section v-if="myDetail" class="card">
        <div class="team-header">
          <div>
            <h2 class="team-name">{{ myDetail.team.name }}</h2>
            <p class="muted">{{ myDetail.team.member_count }} 位成员</p>
          </div>
          <button type="button" class="btn danger sm" @click="leaveTeam">退出</button>
        </div>

        <div class="info-row">
          <span class="badge">自然月缺卡 &gt; {{ myDetail.team.auto_kick_miss_gt }} 天自动移出</span>
        </div>
        <p class="mono-id">ID：{{ myDetail.team.team_id }}</p>

        <!-- 队内统计 -->
        <div class="stat-section">
          <div class="stat-title-row">
            <span class="sub">队内数据</span>
            <MobileSelect
              v-model="statPeriod"
              label=""
              sheet-title="统计周期"
              :options="statPeriodOptions"
              class="period-sel"
            />
          </div>
          <div v-if="stat" class="stat-grid">
            <div class="stat-box">
              <p class="stat-label">鹿次数</p>
              <p class="stat-num">{{ stat.record_count }}</p>
            </div>
            <div class="stat-box">
              <p class="stat-label">鹿率</p>
              <p class="stat-num">{{ (stat.deer_rate * 100).toFixed(1) }}%</p>
            </div>
            <div class="stat-box full">
              <p class="stat-label">统计区间</p>
              <p class="mono sm">{{ stat.range_start }} ~ {{ stat.range_end }}</p>
            </div>
          </div>
        </div>

        <!-- 成员列表 -->
        <div class="member-section">
          <p class="sub">成员（{{ myDetail.members.length }}）</p>
          <ul class="mem-list">
            <li v-for="m in myDetail.members" :key="m.user_id" class="mem-item">
              <span class="mem-id">···{{ m.user_id.slice(-6) }}</span>
              <span class="mem-date muted">{{ m.joined_local_date }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- 未加入任何小组 -->
      <section v-else-if="!myLoading" class="card empty-card">
        <div class="empty-icon">👥</div>
        <p class="empty-title">还没有加入小组</p>
        <p class="muted">点击右下角 + 创建小组，或前往小组广场搜索并申请加入</p>
      </section>

      <!-- FAB 创建按钮 -->
      <button type="button" class="fab" aria-label="创建小组" @click="openCreate">
        <svg viewBox="0 0 24 24" fill="none" width="26" height="26" aria-hidden="true">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
      </button>
    </template>

    <!-- ══════════ 小组广场 ══════════ -->
    <template v-if="tab === 'plaza'">
      <!-- 搜索框 -->
      <div class="search-wrap">
        <svg class="search-icon" viewBox="0 0 20 20" fill="none" width="16" height="16" aria-hidden="true">
          <circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" stroke-width="1.6"/>
          <path d="M13.5 13.5L17 17" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        <input
          v-model="searchQ"
          type="search"
          class="search-input"
          placeholder="搜索小组名称"
          autocomplete="off"
          @input="onSearch"
        />
      </div>

      <p v-if="plazaErr" class="err">{{ plazaErr }}</p>
      <p v-if="plazaLoading && plazaList.length === 0" class="muted center">载入中…</p>
      <p v-if="!plazaLoading && plazaList.length === 0 && !plazaErr" class="muted center">暂无小组</p>

      <!-- 小组卡片列表 -->
      <ul class="plaza-list">
        <li v-for="t in plazaList" :key="t.team_id" class="plaza-card">
          <div class="plaza-info">
            <p class="plaza-name">{{ t.name }}</p>
            <div class="plaza-meta">
              <span class="tag">{{ t.member_count }} 人</span>
              <span class="tag muted">缺卡 &gt; {{ t.auto_kick_miss_gt }} 天移出</span>
            </div>
            <p v-if="joinErrMap[t.team_id]" class="join-err">{{ joinErrMap[t.team_id] }}</p>
          </div>
          <div class="plaza-action">
            <span v-if="t.is_mine" class="joined-badge">已加入</span>
            <button
              v-else
              type="button"
              class="btn primary sm"
              :disabled="isInAnyTeam || joiningId === t.team_id"
              @click="joinTeam(t.team_id)"
            >
              {{ joiningId === t.team_id ? "…" : "申请加入" }}
            </button>
          </div>
        </li>
      </ul>
    </template>
  </div>

  <!-- ══════════ 创建小组弹层 ══════════ -->
  <Teleport to="body">
    <Transition name="sheet-fade">
      <div v-if="showCreate" class="sheet-overlay" @click.self="closeCreate">
        <div class="sheet" role="dialog" aria-modal="true" aria-label="创建小组">
          <div class="sheet-header">
            <button type="button" class="sheet-cancel" @click="closeCreate">取消</button>
            <span class="sheet-title">创建小组</span>
            <button
              type="button"
              class="sheet-submit"
              :disabled="createSubmitting || !createName.trim()"
              @click="submitCreate"
            >
              {{ createSubmitting ? "…" : "创建" }}
            </button>
          </div>
          <div class="sheet-body">
            <div class="field-block">
              <label class="field-label" for="create-name">小组名称</label>
              <input
                id="create-name"
                ref="createNameRef"
                v-model="createName"
                class="field-input"
                maxlength="32"
                placeholder="给你的小组起个名字"
                autocomplete="off"
              />
            </div>
            <div class="field-block">
              <label class="field-label" for="create-kick">自然月缺卡天数上限</label>
              <div class="kick-row">
                <input
                  id="create-kick"
                  v-model.number="createKick"
                  class="field-input kick-input"
                  type="number"
                  min="0"
                  max="31"
                  autocomplete="off"
                />
                <span class="kick-unit muted">天（超出自动移出成员）</span>
              </div>
            </div>
            <p class="hint muted">同一时间只能加入一个小组，小组榜仅统计 ≥10 人的队伍。</p>
            <p v-if="createErr" class="err">{{ createErr }}</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.teams {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 80px;
}

/* ─── Tab 切换 ─── */
.tab-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.tab-pill {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--card-border);
  background: rgba(0, 0, 0, 0.04);
  color: var(--muted);
  font-size: 14px;
  font-weight: 700;
  transition: background 0.18s, color 0.18s, border-color 0.18s;
  -webkit-tap-highlight-color: transparent;
}

.tab-pill.active {
  color: var(--text);
  border-color: rgba(2, 132, 199, 0.42);
  background: rgba(2, 132, 199, 0.10);
}

.tab-pill:active {
  transform: scale(0.98);
}

/* ─── 通用 ─── */
.card {
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.muted {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
}

.center {
  text-align: center;
  padding: 24px 0;
}

.err {
  color: var(--danger);
  font-size: 13px;
  margin: 0;
}

.sub {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.mono-id {
  font-family: ui-monospace, monospace;
  font-size: 11px;
  color: var(--muted);
  margin: 0;
}

.sm {
  font-size: 11px;
}

.btn {
  border-radius: 10px;
  border: 1px solid var(--card-border);
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.05);
  color: var(--text);
  transition: opacity 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.btn.primary {
  border: none;
  background: var(--accent-a);
  color: #fff;
}

.btn.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: transparent;
  color: var(--danger);
}

.btn.sm {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 8px;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ─── 我的小组卡片 ─── */
.team-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.team-name {
  margin: 0 0 2px;
  font-size: 18px;
  font-weight: 800;
}

.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.badge {
  display: inline-block;
  font-size: 11px;
  color: var(--muted);
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  padding: 3px 8px;
}

/* ─── 统计 ─── */
.stat-section {
  border-top: 1px solid var(--card-border);
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.period-sel {
  width: 90px;
  flex-shrink: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-box {
  background: var(--bg);
  border-radius: 10px;
  padding: 10px 12px;
}

.stat-box.full {
  grid-column: 1 / -1;
}

.stat-label {
  margin: 0;
  font-size: 11px;
  color: var(--muted);
}

.stat-num {
  margin: 4px 0 0;
  font-size: 24px;
  font-weight: 900;
  color: var(--accent-b);
}

/* ─── 成员 ─── */
.member-section {
  border-top: 1px solid var(--card-border);
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mem-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mem-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  padding: 5px 8px;
  border-radius: 8px;
  background: var(--bg);
}

.mem-id {
  font-family: ui-monospace, monospace;
  color: var(--text);
}

.mem-date {
  font-variant-numeric: tabular-nums;
}

/* ─── 空状态 ─── */
.empty-card {
  align-items: center;
  text-align: center;
  padding: 32px 20px;
  gap: 8px;
}

.empty-icon {
  font-size: 40px;
  line-height: 1;
}

.empty-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

/* ─── FAB ─── */
.fab {
  position: fixed;
  right: 20px;
  bottom: calc(88px + var(--safe-bottom, 0px));
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent-a);
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.15s, background 0.15s;
  z-index: 50;
  -webkit-tap-highlight-color: transparent;
}

.fab:active {
  transform: scale(0.93);
}

/* ─── 广场搜索 ─── */
.search-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 0 12px;
}

.search-icon {
  flex-shrink: 0;
  color: var(--muted);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 11px 0;
  font-size: 14px;
  color: var(--text);
  outline: none;
}

.search-input::placeholder {
  color: var(--muted);
}

/* ─── 广场卡片列表 ─── */
.plaza-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plaza-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
}

.plaza-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.plaza-name {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plaza-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  font-size: 11px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  padding: 2px 7px;
}

.tag.muted {
  color: var(--muted);
  background: transparent;
  padding-left: 0;
}

.plaza-action {
  flex-shrink: 0;
}

.joined-badge {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-a);
  background: rgba(22, 163, 74, 0.1);
  border-radius: 8px;
  padding: 5px 10px;
}

.join-err {
  margin: 0;
  font-size: 11px;
  color: var(--danger);
}

/* ─── 创建弹层 ─── */
.sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: var(--safe-bottom, 0);
}

.sheet {
  width: 100%;
  max-width: 480px;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-bottom: none;
  border-radius: 22px 22px 0 0;
  display: flex;
  flex-direction: column;
  max-height: 88vh;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.10);
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}

.sheet-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
}

.sheet-cancel {
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 600;
  color: var(--muted);
  padding: 4px 0;
  min-width: 44px;
  text-align: left;
}

.sheet-submit {
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 700;
  color: var(--accent-a);
  padding: 4px 0;
  min-width: 44px;
  text-align: right;
  transition: opacity 0.15s;
}

.sheet-submit:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.sheet-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
}

.field-input {
  width: 100%;
  padding: 11px 14px;
  border-radius: 12px;
  border: 1px solid var(--card-border);
  background: rgba(0, 0, 0, 0.04);
  color: var(--text);
  font-size: 15px;
  outline: none;
  transition: border-color 0.18s;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: rgba(2, 132, 199, 0.4);
}

.kick-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kick-input {
  width: 80px;
}

.kick-unit {
  font-size: 13px;
}

.hint {
  font-size: 12px;
  line-height: 1.6;
}

/* ─── 动画 ─── */
.sheet-fade-enter-active,
.sheet-fade-leave-active {
  transition: opacity 0.22s ease;
}

.sheet-fade-enter-active .sheet,
.sheet-fade-leave-active .sheet {
  transition: transform 0.22s cubic-bezier(0.32, 0.72, 0, 1);
}

.sheet-fade-enter-from,
.sheet-fade-leave-to {
  opacity: 0;
}

.sheet-fade-enter-from .sheet,
.sheet-fade-leave-to .sheet {
  transform: translateY(100%);
}
</style>
