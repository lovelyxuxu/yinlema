import { computed, ref } from "vue";
import { apiFetch } from "../api/client";

export interface LuRecord {
  id: string;
  timestamp: number; // ms since epoch
  date: string;      // YYYY-MM-DD
}

interface ApiRecord {
  record_id: string;
  user_id: string;
  timestamp: string; // ISO8601
  date: string;
  note: string;
  created_at: string;
}

function toLocal(r: ApiRecord): LuRecord {
  return {
    id: r.record_id,
    timestamp: new Date(r.timestamp).getTime(),
    date: r.date,
  };
}

function dateStr(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function today(): string {
  return dateStr(new Date());
}

/* ── 模块级单例状态 ── */
const records = ref<LuRecord[]>([]);
const loading = ref(false);
let _fetched = false; // 避免重复拉取

async function fetchRecords(): Promise<void> {
  if (_fetched) return;
  loading.value = true;
  try {
    const data = await apiFetch<ApiRecord[]>("/records?limit=200");
    records.value = data.map(toLocal);
    _fetched = true;
  } finally {
    loading.value = false;
  }
}

/** 用户退出时重置状态，供 auth logout 调用 */
export function resetRecords(): void {
  records.value = [];
  _fetched = false;
}

/* ── 统计计算（与原版逻辑一致） ── */

function countOnDate(date: string): number {
  return records.value.filter((r) => r.date === date).length;
}

export const streakDays = computed(() => {
  const set = new Set(records.value.map((r) => r.date));
  if (set.has(today())) return 0;
  let count = 0;
  const d = new Date();
  d.setDate(d.getDate() - 1);
  while (!set.has(dateStr(d))) {
    count++;
    d.setDate(d.getDate() - 1);
    if (count > 1095) break;
  }
  return count;
});

export function countByDay(n = 7): { date: string; count: number }[] {
  const result: { date: string; count: number }[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const date = dateStr(d);
    result.push({ date, count: countOnDate(date) });
  }
  return result;
}

export function countByWeek(n = 6): { label: string; count: number }[] {
  const result: { label: string; count: number }[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const end = new Date();
    end.setDate(end.getDate() - i * 7);
    const start = new Date(end);
    start.setDate(start.getDate() - 6);
    let count = 0;
    for (let j = 0; j <= 6; j++) {
      const d = new Date(start);
      d.setDate(d.getDate() + j);
      count += countOnDate(dateStr(d));
    }
    result.push({ label: `${start.getMonth() + 1}/${start.getDate()}`, count });
  }
  return result;
}

export function countByMonth(n = 6): { label: string; count: number }[] {
  const result: { label: string; count: number }[] = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const prefix = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    const count = records.value.filter((r) => r.date.startsWith(prefix)).length;
    result.push({ label: `${d.getMonth() + 1}月`, count });
  }
  return result;
}

export const recentFrequency = computed(() => {
  const days = countByDay(7);
  const total = days.reduce((s, d) => s + Math.min(d.count, 1), 0);
  return total / 7;
});

/* ── useRecords ── */

export function useRecords() {
  async function addRecord(): Promise<void> {
    const now = new Date();
    const data = await apiFetch<ApiRecord>("/records", {
      method: "POST",
      body: { timestamp: now.toISOString(), note: "" },
    });
    records.value = [toLocal(data), ...records.value];
  }

  async function removeRecord(id: string): Promise<void> {
    await apiFetch<null>(`/records/${id}`, { method: "DELETE" });
    records.value = records.value.filter((r) => r.id !== id);
  }

  async function removeLatest(): Promise<void> {
    if (records.value.length === 0) return;
    const latest = records.value[0];
    await removeRecord(latest.id);
  }

  const todayCount = computed(() => countOnDate(today()));

  return {
    records,
    loading,
    fetchRecords,
    addRecord,
    removeRecord,
    removeLatest,
    streakDays,
    todayCount,
    recentFrequency,
    countByDay,
    countByWeek,
    countByMonth,
  };
}
