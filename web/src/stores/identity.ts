import { computed, ref } from "vue";
import { apiFetch } from "../api/client";
import { isLoggedIn } from "./auth";

export type IdentityRoleId =
  | "balanced"
  | "sigma"
  | "chaos"
  | "pure"
  | "max"
  | "moka"
  | "fan"
  | "cat"
  | "random";

export type LustTier = "calm" | "low" | "mid" | "high" | "max" | "chaos";

export interface IdentityRole {
  id: IdentityRoleId;
  label: string;
  emoji: string;
  luProbability: number | null;
  description: string;
  flavor: string;
  lustTier: LustTier;
}

const ROLE_DEFINITIONS: IdentityRole[] = [
  {
    id: "balanced",
    label: "表面清纯",
    emoji: "🙂",
    luProbability: 0.5,
    description: "一半一半，交给命运。",
    flavor: "看起来人畜无害，实际上随缘手滑。",
    lustTier: "mid",
  },
  {
    id: "sigma",
    label: "戒断菩萨（假的）",
    emoji: "🪷",
    luProbability: 0.1,
    description: "嘴上戒断，心里随缘。",
    flavor: "瘾运极低，但也不是没有。",
    lustTier: "low",
  },
  {
    id: "chaos",
    label: "深夜 emo 选手",
    emoji: "🌙",
    luProbability: 0.85,
    description: "夜晚加成，懂的都懂。",
    flavor: "今日手气检定容易「手痒」。",
    lustTier: "high",
  },
  {
    id: "pure",
    label: "清心道姑",
    emoji: "🧘",
    luProbability: 0,
    description: "今日检定，稳住能赢。",
    flavor: "瘾运归零，心湖无波。",
    lustTier: "calm",
  },
  {
    id: "max",
    label: "瘾运拉满",
    emoji: "🔥",
    luProbability: 1,
    description: "今日检定，大概率手痒。",
    flavor: "心河漫堤，懂的都懂。",
    lustTier: "max",
  },
  {
    id: "moka",
    label: "摸鱼少女",
    emoji: "🐟",
    luProbability: 0.3,
    description: "上班正经，下班随缘。",
    flavor: "瘾运不高，但架不住会摸。",
    lustTier: "low",
  },
  {
    id: "fan",
    label: "狂热信徒",
    emoji: "✨",
    luProbability: 0.95,
    description: "几乎必手滑，留一点奇迹。",
    flavor: "魅魔心常亮。",
    lustTier: "max",
  },
  {
    id: "cat",
    label: "懒猫趴趴",
    emoji: "🐱",
    luProbability: 0.15,
    description: "能躺绝不卷。",
    flavor: "偶尔伸爪，多数在趴。",
    lustTier: "low",
  },
  {
    id: "random",
    label: "天选骰子",
    emoji: "🎲",
    luProbability: null,
    description: "每次检定随机抽一档瘾运。",
    flavor: "瘾运 ??%，命运自己掷。",
    lustTier: "chaos",
  },
];

/** 展示顺序：天选骰子首位，其余按瘾运从低到高 */
const RANDOM_ROLE = ROLE_DEFINITIONS.find((r) => r.id === "random")!;
const FIXED_SORTED = ROLE_DEFINITIONS.filter((r) => r.id !== "random").sort(
  (a, b) => (a.luProbability ?? 0) - (b.luProbability ?? 0),
);

export const ROLES: IdentityRole[] = [RANDOM_ROLE, ...FIXED_SORTED];

export const FIXED_ROLES = FIXED_SORTED;

export function displayLuPercent(role: IdentityRole): string {
  if (role.luProbability === null) return "??%";
  return `${Math.round(role.luProbability * 100)}%`;
}

export function riverWidthPercent(role: IdentityRole): number {
  if (role.id === "random") return 100;
  if (role.luProbability === null) return 100;
  if (role.luProbability >= 1) return 100;
  return Math.round(role.luProbability * 100);
}

export function pickRandomFixedRole(): IdentityRole {
  const i = Math.floor(Math.random() * FIXED_ROLES.length);
  return FIXED_ROLES[i]!;
}

const STORAGE_KEY = "yinlema:identity-role";

const stored = localStorage.getItem(STORAGE_KEY) as IdentityRoleId | null;
const storedValid = stored && ROLES.some((r) => r.id === stored);

const activeId = ref<IdentityRoleId>(storedValid ? stored! : "balanced");

export function initIdentityFromServer(role: IdentityRoleId): void {
  activeId.value = role;
  localStorage.setItem(STORAGE_KEY, role);
}

export function useIdentity() {
  const roles = ROLES;

  const activeRole = computed(
    () => ROLES.find((r) => r.id === activeId.value) ?? ROLES[0],
  );

  async function setRole(id: IdentityRoleId): Promise<void> {
    activeId.value = id;
    localStorage.setItem(STORAGE_KEY, id);

    if (isLoggedIn.value) {
      try {
        await apiFetch("/users/me/identity", {
          method: "PUT",
          body: { identity_role: id },
        });
      } catch {
        /* 本地已更新 */
      }
    }
  }

  return { roles, activeRole, setRole };
}
