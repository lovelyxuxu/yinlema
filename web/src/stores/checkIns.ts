import { ref } from "vue";
import { apiFetch } from "../api/client";

export type CheckInStatus = "deer" | "none";
export type TodayCheckInStatus = CheckInStatus | null;

export interface CheckInMonth {
  year: number;
  month: number;
  days: Record<string, CheckInStatus>;
}

/** 上海日历日 YYYY-MM-DD（与后端 dates_cn 一致） */
export function todayShanghai(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
}

const _todayStatus = ref<TodayCheckInStatus>(null);
/** 近期打卡（供首页图表合并「补卡鹿了」等无 records 的日期） */
const _checkInDaysMap = ref<Record<string, CheckInStatus>>({});

export const todayCheckInStatus = _todayStatus;
export const checkInDaysMap = _checkInDaysMap;

function shanghaiYearMonth(): { year: number; month: number } {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "numeric",
  }).formatToParts(new Date());
  return {
    year: Number(parts.find((p) => p.type === "year")?.value),
    month: Number(parts.find((p) => p.type === "month")?.value),
  };
}

/** 拉取最近若干自然月打卡，写入 checkInDaysMap */
export async function loadRecentCheckIns(monthCount = 7): Promise<void> {
  let { year, month } = shanghaiYearMonth();
  const merged: Record<string, CheckInStatus> = {};
  for (let i = 0; i < monthCount; i++) {
    try {
      const cal = await fetchCheckInMonth(year, month);
      Object.assign(merged, cal.days);
    } catch {
      /* 单月失败不阻断 */
    }
    month -= 1;
    if (month < 1) {
      month = 12;
      year -= 1;
    }
  }
  _checkInDaysMap.value = merged;
  const today = todayShanghai();
  const s = merged[today];
  _todayStatus.value = s === "deer" || s === "none" ? s : null;
}

export function statusText(status: TodayCheckInStatus): string {
  if (status === "deer") return "今日打卡：鹿了";
  if (status === "none") return "今日打卡：没鹿";
  return "今日打卡：未打卡";
}

export async function fetchCheckInMonth(year: number, month: number): Promise<CheckInMonth> {
  const q = new URLSearchParams({ year: String(year), month: String(month) });
  return apiFetch<CheckInMonth>(`/check-ins/month?${q.toString()}`);
}

export async function upsertCheckIn(
  status: CheckInStatus,
  localDate?: string | null,
): Promise<void> {
  await apiFetch("/check-ins", {
    method: "POST",
    body: {
      status,
      local_date: localDate && localDate.trim() ? localDate.trim() : null,
    },
  });
}

export async function refreshTodayStatus(): Promise<TodayCheckInStatus> {
  const now = new Date();
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "numeric",
  }).formatToParts(now);
  const year = Number(parts.find((p) => p.type === "year")?.value);
  const month = Number(parts.find((p) => p.type === "month")?.value);
  const today = todayShanghai();

  try {
    const cal = await fetchCheckInMonth(year, month);
    const s = cal.days[today];
    _todayStatus.value = s === "deer" || s === "none" ? s : null;
  } catch {
    _todayStatus.value = null;
  }
  return _todayStatus.value;
}
