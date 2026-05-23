import { computed, ref } from "vue";
import { apiFetch } from "../api/client";
import { isLoggedIn } from "./auth";

export type IdentityRoleId = "balanced" | "sigma" | "chaos";

export interface IdentityRole {
  id: IdentityRoleId;
  label: string;
  emoji: string;
  luProbability: number;
  description: string;
  flavor: string;
}

const ROLES: IdentityRole[] = [
  {
    id: "balanced",
    label: "表面清纯",
    emoji: "🙂",
    luProbability: 0.5,
    description: "一半一半，交给命运。",
    flavor: "看起来人畜无害，实际上随缘手滑。",
  },
  {
    id: "sigma",
    label: "戒断菩萨（假的）",
    emoji: "🪷",
    luProbability: 0.1,
    description: "嘴上戒断，心里随缘。",
    flavor: "瘾运极低，但也不是没有。",
  },
  {
    id: "chaos",
    label: "深夜 emo 选手",
    emoji: "🌙",
    luProbability: 0.85,
    description: "夜晚加成，懂的都懂。",
    flavor: "今日手气检定容易「手痒」。",
  },
];

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
