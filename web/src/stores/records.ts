import { computed, ref } from "vue";
import { apiFetch } from "../api/client";

export interface HabitRecord {
  id: string;
  timestamp: number;
  date: string;
  note: string;
}

interface ApiRecord {
  record_id: string;
  user_id: string;
  habit_type?: string;
  timestamp: string;
  date: string;
  note: string;
  created_at: string;
}

interface ApiStats {
  streak_days_no_record: number;
  since_last_ms: number | null;
  today_count: number;
  longest_streak_no_record: number;
  recent_frequency: number;
  by_day: { date: string; count: number }[];
  by_week: { label: string; count: number }[];
  by_month: { label: string; count: number }[];
}

function toLocal(r: ApiRecord): HabitRecord {
  return {
    id: r.record_id,
    timestamp: new Date(r.timestamp).getTime(),
    date: r.date,
    note: r.note,
  };
}

const TZ_SHANGHAI = "Asia/Shanghai";

function formatShanghaiDate(d: Date): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: TZ_SHANGHAI }).format(d);
}

function today(): string {
  return formatShanghaiDate(new Date());
}

const records = ref<HabitRecord[]>([]);
const loading = ref(false);
const stats = ref<ApiStats | null>(null);
let _fetched = false;

async function fetchStats(): Promise<void> {
  stats.value = await apiFetch<ApiStats>("/records/stats");
}

async function fetchRecords(): Promise<void> {
  if (_fetched) return;
  loading.value = true;
  try {
    const data = await apiFetch<ApiRecord[]>("/records?limit=1000");
    records.value = data.map(toLocal);
    await fetchStats();
    _fetched = true;
  } finally {
    loading.value = false;
  }
}

export async function refreshRecords(): Promise<void> {
  _fetched = false;
  await fetchRecords();
}

export function resetRecords(): void {
  records.value = [];
  stats.value = null;
  _fetched = false;
}

function countOnDate(date: string): number {
  return records.value.filter((r) => r.date === date).length;
}

export function countByDay(n = 7): { date: string; count: number }[] {
  const result: { date: string; count: number }[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const date = formatShanghaiDate(d);
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
      count += countOnDate(formatShanghaiDate(d));
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

export function countByYear(n = 6): { year: number; label: string; count: number }[] {
  const result: { year: number; label: string; count: number }[] = [];
  const currentYear = new Date().getFullYear();
  for (let i = n - 1; i >= 0; i--) {
    const y = currentYear - i;
    const count = records.value.filter((r) => r.date.startsWith(`${y}-`)).length;
    result.push({ year: y, label: `${y}年`, count });
  }
  return result;
}

export const recentFrequency = computed(
  () => stats.value?.recent_frequency ?? 0,
);

export function useRecords() {
  const streakDaysNoRecord = computed(
    () => stats.value?.streak_days_no_record ?? 0,
  );
  const sinceLastMs = computed(() => stats.value?.since_last_ms ?? null);
  const todayCount = computed(
    () => stats.value?.today_count ?? countOnDate(today()),
  );

  const sinceLastLabel = computed(() => {
    const ms = sinceLastMs.value;
    if (ms == null) return "还没有记录，点下面开始";
    const h = Math.floor(ms / 3_600_000);
    const d = Math.floor(h / 24);
    const rh = h % 24;
    return `上次翻车至今 ${d} 天 ${rh} 小时`;
  });

  async function addRecord(): Promise<void> {
    const now = new Date();
    const data = await apiFetch<ApiRecord>("/records", {
      method: "POST",
      body: { timestamp: now.toISOString(), note: "" },
    });
    records.value = [toLocal(data), ...records.value];
    await fetchStats();
  }

  async function addRecordForDate(localDate: string): Promise<void> {
    const timestamp = `${localDate}T12:00:00+08:00`;
    const data = await apiFetch<ApiRecord>("/records", {
      method: "POST",
      body: { timestamp, note: "" },
    });
    records.value = [toLocal(data), ...records.value];
    await fetchStats();
  }

  async function removeRecord(id: string): Promise<void> {
    await apiFetch<null>(`/records/${id}`, { method: "DELETE" });
    records.value = records.value.filter((r) => r.id !== id);
    await fetchStats();
  }

  async function removeLatest(): Promise<void> {
    if (records.value.length === 0) return;
    await removeRecord(records.value[0].id);
  }

  async function updateNote(id: string, note: string): Promise<void> {
    await apiFetch<ApiRecord>(`/records/${id}`, {
      method: "PATCH",
      body: { note },
    });
    records.value = records.value.map((r) => (r.id === id ? { ...r, note } : r));
  }

  return {
    records,
    loading,
    fetchRecords,
    refreshRecords,
    addRecord,
    addRecordForDate,
    removeRecord,
    removeLatest,
    updateNote,
    streakDaysNoRecord,
    sinceLastMs,
    sinceLastLabel,
    todayCount,
    recentFrequency,
    countByDay,
    countByWeek,
    countByMonth,
    countByYear,
  };
}
