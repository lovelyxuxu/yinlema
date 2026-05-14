import { computed, ref } from "vue";

export type IdentityRoleId = "balanced" | "sigma" | "chaos";

export interface IdentityRole {
  id: IdentityRoleId;
  label: string;
  /** 随机到「鹿」的概率，0–1 */
  luProbability: number;
  description: string;
}

const ROLES: IdentityRole[] = [
  {
    id: "balanced",
    label: "平常心",
    luProbability: 0.5,
    description: "一半一半，交给命运。",
  },
  {
    id: "sigma",
    label: "西格玛男人",
    luProbability: 0.01,
    description: "自律拉满，几乎不鹿。",
  },
  {
    id: "chaos",
    label: "混沌乐子人",
    luProbability: 0.85,
    description: "世界很大，先鹿为敬。",
  },
];

const STORAGE_KEY = "lulemo:identity-role";

const stored = localStorage.getItem(STORAGE_KEY) as IdentityRoleId | null;
const storedValid = stored && ROLES.some((r) => r.id === stored);

const activeId = ref<IdentityRoleId>(storedValid ? stored! : "balanced");

function persist() {
  localStorage.setItem(STORAGE_KEY, activeId.value);
}

export function useIdentity() {
  const roles = ROLES;

  const activeRole = computed(
    () => ROLES.find((r) => r.id === activeId.value) ?? ROLES[0],
  );

  function setRole(id: IdentityRoleId) {
    activeId.value = id;
    persist();
  }

  return { roles, activeRole, setRole };
}
