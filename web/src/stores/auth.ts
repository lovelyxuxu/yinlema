import { computed, ref } from "vue";
import { apiFetch, ApiError, getStoredToken, saveToken, removeToken } from "../api/client";

export type IdentityRoleId = "balanced" | "sigma" | "chaos";

export interface UserInfo {
  user_id: string;
  username: string;
  identity_role: IdentityRoleId;
  created_at: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
  identity_role: string;
}

/* ── 模块级单例状态 ── */
const _token = ref<string | null>(getStoredToken());
const _user = ref<UserInfo | null>(null);

export const isLoggedIn = computed(() => !!_token.value);

function applyTokenResponse(data: TokenResponse): void {
  _token.value = data.access_token;
  saveToken(data.access_token);
  _user.value = {
    user_id: data.user_id,
    username: data.username,
    identity_role: data.identity_role as IdentityRoleId,
    created_at: "",
  };
}

export function useAuth() {
  async function register(username: string, password: string): Promise<void> {
    const data = await apiFetch<TokenResponse>("/auth/register", {
      method: "POST",
      body: { username, password },
      token: null,
    });
    applyTokenResponse(data);
  }

  async function login(username: string, password: string): Promise<void> {
    const data = await apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: { username, password },
      token: null,
    });
    applyTokenResponse(data);
  }

  /** 用已有 token 拉取用户信息（应用启动时调用） */
  async function fetchMe(): Promise<boolean> {
    if (!_token.value) return false;
    try {
      const data = await apiFetch<UserInfo>("/auth/me");
      _user.value = data;
      return true;
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        logout();
      }
      return false;
    }
  }

  function logout(): void {
    _token.value = null;
    _user.value = null;
    removeToken();
  }

  return {
    token: _token,
    user: _user,
    isLoggedIn,
    register,
    login,
    logout,
    fetchMe,
  };
}
