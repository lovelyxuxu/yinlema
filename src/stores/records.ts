import { computed, ref } from "vue";

export interface LuRecord {
  id: string;
  timestamp: number;
  date: string; // YYYY-MM-DD
}

const STORAGE_KEY = "lulemo:records";

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function dateStr(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function save(list: LuRecord[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

/** 轻量确定性伪随机，seed 相同则结果一致 */
function seededRand(seed: number): number {
  const x = Math.sin(seed + 1) * 10000;
  return x - Math.floor(x);
}

/**
 * 首次打开时自动填充约 90 天演示历史数据，让图表与连续天数即刻有内容可看。
 * 若 localStorage 已有数据则跳过。
 */
function seedDemoData(): LuRecord[] {
  const list: LuRecord[] = [];

  // 各阶段每天鹿的概率（0 = 不鹿，1 = 必鹿）
  // daysAgo 越大越早，最近 3 天保持干净以展示连续天数
  const phaseProb = (daysAgo: number): number => {
    if (daysAgo <= 3)  return 0;     // 最近 3 天没鹿，streak = 3
    if (daysAgo <= 7)  return 0.30;  // 上周偶尔
    if (daysAgo <= 21) return 0.45;  // 近三周适中
    if (daysAgo <= 42) return 0.55;  // 一两月前稍频繁
    return 0.60;                     // 更早期频率最高
  };

  for (let daysAgo = 90; daysAgo >= 1; daysAgo--) {
    const prob = phaseProb(daysAgo);
    const rand1 = seededRand(daysAgo * 7);
    if (rand1 >= prob) continue; // 当天不鹿

    // 确定当天鹿几次（偶尔 2 次）
    const times = seededRand(daysAgo * 13) < 0.15 ? 2 : 1;

    for (let t = 0; t < times; t++) {
      const base = new Date();
      base.setHours(0, 0, 0, 0);
      base.setDate(base.getDate() - daysAgo);
      // 给每条记录一个随机时间（8:00 ~ 23:00）
      const hourOffset = Math.floor(seededRand(daysAgo * 17 + t * 3) * 15 + 8) * 3600000;
      const minOffset  = Math.floor(seededRand(daysAgo * 19 + t * 5) * 60) * 60000;
      const ts = base.getTime() + hourOffset + minOffset;
      const d = new Date(ts);
      list.push({
        id: `demo-${daysAgo}-${t}`,
        timestamp: ts,
        date: d.toISOString().slice(0, 10),
      });
    }
  }

  // 按时间倒序排列（最新在前）
  list.sort((a, b) => b.timestamp - a.timestamp);
  save(list);
  return list;
}

function loadOrSeed(): LuRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as LuRecord[];
  } catch {
    // ignore
  }
  return seedDemoData();
}

const records = ref<LuRecord[]>(loadOrSeed());

export const streakDays = computed(() => {
  const set = new Set(records.value.map((r) => r.date));
  let count = 0;
  const d = new Date();
  // If already recorded today, streak is 0
  if (set.has(dateStr(d))) return 0;
  d.setDate(d.getDate() - 1);
  while (set.has(dateStr(d)) === false) {
    count++;
    d.setDate(d.getDate() - 1);
    // Safety: stop at 3 years
    if (count > 1095) break;
  }
  return count;
});

/** Total records on a given YYYY-MM-DD date */
function countOnDate(date: string): number {
  return records.value.filter((r) => r.date === date).length;
}

/** Last n days stats: returns array of { date, count } ordered oldest→newest */
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

/** Last n weeks stats: returns array of { label, count } ordered oldest→newest */
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
    const label = `${start.getMonth() + 1}/${start.getDate()}`;
    result.push({ label, count });
  }
  return result;
}

/** Last n months stats: returns array of { label, count } ordered oldest→newest */
export function countByMonth(n = 6): { label: string; count: number }[] {
  const result: { label: string; count: number }[] = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const year = d.getFullYear();
    const month = d.getMonth();
    const prefix = `${year}-${String(month + 1).padStart(2, "0")}`;
    const count = records.value.filter((r) => r.date.startsWith(prefix)).length;
    result.push({ label: `${month + 1}月`, count });
  }
  return result;
}

/** 近 7 天平均频率，返回 0~1 */
export const recentFrequency = computed(() => {
  const days = countByDay(7);
  const total = days.reduce((s, d) => s + Math.min(d.count, 1), 0);
  return total / 7;
});

export function useRecords() {
  function addRecord() {
    const now = new Date();
    const rec: LuRecord = {
      id: `${now.getTime()}-${Math.random().toString(36).slice(2, 7)}`,
      timestamp: now.getTime(),
      date: dateStr(now),
    };
    records.value = [rec, ...records.value];
    save(records.value);
    return rec;
  }

  function removeRecord(id: string) {
    records.value = records.value.filter((r) => r.id !== id);
    save(records.value);
  }

  function removeLatest() {
    if (records.value.length === 0) return;
    records.value = records.value.slice(1);
    save(records.value);
  }

  const todayCount = computed(() => countOnDate(today()));

  return {
    records,
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
