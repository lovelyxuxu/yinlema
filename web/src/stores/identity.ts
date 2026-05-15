import { computed, ref } from "vue";
import { apiFetch } from "../api/client";
import { isLoggedIn } from "./auth";

export type IdentityRoleId = "balanced" | "sigma" | "chaos";

export interface IdentityRole {
  id: IdentityRoleId;
  label: string;
  emoji: string;
  /** 随机到「鹿」的概率，0–1 */
  luProbability: number;
  description: string;
  flavor: string;
}

const ROLES: IdentityRole[] = [
  {
    id: "balanced",
    label: "平常心",
    emoji: "🧘",
    luProbability: 0.5,
    description: "一半一半，交给命运。",
    flavor: "不执着于结果，顺其自然，今天怎样都好。",
  },
  {
    id: "sigma",
    label: "西格玛男人",
    emoji: "🔱",
    luProbability: 0.01,
    description: "自律拉满，几乎不鹿。",
    flavor: "掌控欲望，化能量为动力。真·西格玛只专注于自身的成长。",
  },
  {
    id: "chaos",
    label: "混沌乐子人",
    emoji: "🎲",
    luProbability: 0.85,
    description: "世界很大，先鹿为敬。",
    flavor: "规则是什么？不存在的。今日份快乐必须有。",
  },
];

const STORAGE_KEY = "lulemo:identity-role";

const stored = localStorage.getItem(STORAGE_KEY) as IdentityRoleId | null;
const storedValid = stored && ROLES.some((r) => r.id === stored);

const activeId = ref<IdentityRoleId>(storedValid ? stored! : "balanced");

/** 登录后用服务端角色初始化（不触发 API 同步） */
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
        // 静默失败：本地已更新，下次登录时服务端会以本地为准
      }
    }
  }

  return { roles, activeRole, setRole };
}
