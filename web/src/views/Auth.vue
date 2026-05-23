<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth, type UserRegionPayload } from "../stores/auth";
import { ApiError } from "../api/client";
import { regionData } from "element-china-area-data";
import RegionPicker from "../components/RegionPicker.vue";
import { toSixDigitAdcode } from "../utils/regionAdcode";

type Mode = "login" | "register";

interface AreaItem {
  value: string;
  label: string;
  children?: AreaItem[];
}

const provinces = regionData as unknown as AreaItem[];

const router = useRouter();
const { login, register } = useAuth();

const mode = ref<Mode>("login");
const username = ref("");
const password = ref("");
const confirmPassword = ref("");
const errorMsg = ref("");
const loading = ref(false);

const provinceCode = ref("");
const cityCode = ref("");
const districtCode = ref("");

function buildRegionPayload(): UserRegionPayload | null {
  const pItem = provinces.find((x) => x.value === provinceCode.value);
  const cItem = pItem?.children?.find((x) => x.value === cityCode.value);
  const dItem = cItem?.children?.find((x) => x.value === districtCode.value);
  if (!pItem || !cItem || !dItem) return null;
  return {
    province_code: toSixDigitAdcode(pItem.value),
    city_code: toSixDigitAdcode(cItem.value),
    district_code: toSixDigitAdcode(dItem.value),
    province_name: pItem.label,
    city_name: cItem.label,
    district_name: dItem.label,
  };
}

function switchMode(m: Mode) {
  mode.value = m;
  errorMsg.value = "";
  password.value = "";
  confirmPassword.value = "";
  provinceCode.value = "";
  cityCode.value = "";
  districtCode.value = "";
}

async function submit() {
  errorMsg.value = "";

  if (!username.value.trim() || !password.value) {
    errorMsg.value = "请填写用户名和密码";
    return;
  }

  if (mode.value === "register") {
    if (username.value.trim().length < 3) {
      errorMsg.value = "用户名至少 3 个字符";
      return;
    }
    if (password.value.length < 6) {
      errorMsg.value = "密码至少 6 位";
      return;
    }
    if (password.value !== confirmPassword.value) {
      errorMsg.value = "两次密码不一致";
      return;
    }
    const reg = buildRegionPayload();
    if (!reg) {
      errorMsg.value = "请选择完整的省·市·区";
      return;
    }
  }

  loading.value = true;
  try {
    if (mode.value === "login") {
      await login(username.value.trim(), password.value);
    } else {
      const reg = buildRegionPayload();
      if (!reg) throw new Error("请选择省市区");
      await register(username.value.trim(), password.value, reg);
    }
    router.replace("/");
  } catch (e) {
    if (e instanceof ApiError) {
      if (e.status === 401) errorMsg.value = "用户名或密码错误";
      else if (e.status === 409) errorMsg.value = "用户名已被占用，换一个试试";
      else if (e.status === 422) errorMsg.value = e.detail || "信息格式有误，请检查";
      else errorMsg.value = e.detail || "请求失败，请稍后重试";
    } else {
      errorMsg.value = "网络异常，请确认后端已启动（端口 8000）";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="bg-blob bg-blob-a" aria-hidden="true" />
    <div class="bg-blob bg-blob-b" aria-hidden="true" />

    <div class="auth-card">
      <div class="brand">
        <div class="brand-badge" aria-hidden="true">💗</div>
        <h1 class="brand-name">瘾了吗</h1>
        <p class="brand-sub">姐妹局 · 记一记手滑几次也没事</p>
      </div>

      <div class="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          class="tab"
          :class="{ active: mode === 'login' }"
          @click="switchMode('login')"
        >
          登录
        </button>
        <button
          type="button"
          role="tab"
          class="tab"
          :class="{ active: mode === 'register' }"
          @click="switchMode('register')"
        >
          注册
        </button>
      </div>

      <form class="form" autocomplete="off" @submit.prevent="submit">
        <div class="field">
          <label class="label" for="auth-username">用户名</label>
          <input
            id="auth-username"
            name="yinlema-username"
            v-model="username"
            type="text"
            class="input"
            placeholder="字母 / 数字 / 中文，3～20 位"
            autocomplete="off"
            autocapitalize="off"
            autocorrect="off"
            spellcheck="false"
            :disabled="loading"
            maxlength="20"
          />
        </div>

        <div class="field">
          <label class="label" for="auth-password">密码</label>
          <input
            id="auth-password"
            name="yinlema-password"
            v-model="password"
            type="password"
            class="input"
            placeholder="至少 6 位"
            autocomplete="off"
            :disabled="loading"
            maxlength="64"
          />
        </div>

        <transition name="slide-down">
          <div v-if="mode === 'register'" class="field">
            <label class="label" for="auth-confirm">确认密码</label>
            <input
              id="auth-confirm"
              name="yinlema-password-confirm"
              v-model="confirmPassword"
              type="password"
              class="input"
              placeholder="再输一遍"
              autocomplete="off"
              :disabled="loading"
              maxlength="64"
            />
          </div>
        </transition>

        <transition name="slide-down">
          <div v-if="mode === 'register'" class="region-block">
            <p class="region-label">所在地区（注册必选）</p>
            <RegionPicker
              v-model:province-code="provinceCode"
              v-model:city-code="cityCode"
              v-model:district-code="districtCode"
              :disabled="loading"
            />
          </div>
        </transition>

        <transition name="fade">
          <p v-if="errorMsg" class="error-msg" role="alert">{{ errorMsg }}</p>
        </transition>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner" aria-hidden="true" />
          {{ loading ? "请稍候…" : mode === "login" ? "进入瘾了吗" : "注册并进入" }}
        </button>
      </form>

      <p class="footer-note">内部使用 · 轻松记录 · 不评判只玩梗</p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: max(20px, env(safe-area-inset-top)) 16px max(24px, env(safe-area-inset-bottom));
  position: relative;
  overflow: hidden;
  background: linear-gradient(160deg, #fff1f2 0%, #fdf2f8 35%, #fce7f3 70%, #fbcfe8 100%);
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(48px);
  pointer-events: none;
}
.bg-blob-a {
  width: 220px;
  height: 220px;
  top: -40px;
  right: -60px;
  background: rgba(236, 72, 153, 0.35);
}
.bg-blob-b {
  width: 260px;
  height: 260px;
  bottom: -80px;
  left: -80px;
  background: rgba(192, 132, 252, 0.28);
}

.auth-card {
  position: relative;
  z-index: 1;
  width: min(400px, 100%);
  border-radius: 24px;
  padding: 28px 22px 22px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.85);
  box-shadow:
    0 20px 50px rgba(190, 24, 93, 0.12),
    0 4px 16px rgba(236, 72, 153, 0.08);
}

.brand {
  text-align: center;
  margin-bottom: 24px;
}

.brand-badge {
  width: 52px;
  height: 52px;
  margin: 0 auto 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  border-radius: 16px;
  background: linear-gradient(135deg, #fce7f3, #fbcfe8);
  box-shadow: 0 6px 16px rgba(236, 72, 153, 0.2);
}

.brand-name {
  margin: 0 0 6px;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: 0.06em;
  background: linear-gradient(135deg, #db2777, #ec4899, #c084fc);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.brand-sub {
  margin: 0;
  font-size: 13px;
  color: #9d174d;
  opacity: 0.85;
  line-height: 1.5;
}

.tabs {
  display: flex;
  gap: 6px;
  background: #fce7f3;
  border-radius: 14px;
  padding: 5px;
  margin-bottom: 22px;
}

.tab {
  flex: 1;
  padding: 10px 8px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  background: transparent;
  color: #be185d;
  opacity: 0.65;
  transition: all 0.2s ease;
}

.tab.active {
  background: #fff;
  color: #831843;
  opacity: 1;
  box-shadow: 0 2px 10px rgba(236, 72, 153, 0.15);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: #9d174d;
  font-weight: 700;
}

.input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(190, 24, 93, 0.12);
  background: #fffbff;
  color: var(--text);
  font-size: 15px;
  outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}

.input:focus {
  border-color: rgba(236, 72, 153, 0.55);
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.14);
}

.input::placeholder {
  color: rgba(157, 23, 77, 0.35);
}

.input:disabled {
  opacity: 0.55;
}

.region-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-radius: 14px;
  background: #fdf2f8;
  border: 1px dashed rgba(236, 72, 153, 0.25);
}

.region-label {
  margin: 0;
  font-size: 12px;
  color: #9d174d;
  font-weight: 700;
}

.error-msg {
  margin: 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(225, 29, 72, 0.08);
  border: 1px solid rgba(225, 29, 72, 0.2);
  color: #be123c;
  font-size: 13px;
  line-height: 1.5;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, #ec4899, #f472b6, #fb7185);
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 10px 24px rgba(236, 72, 153, 0.35);
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
  margin-top: 4px;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 12px 28px rgba(236, 72, 153, 0.42);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.footer-note {
  margin: 18px 0 0;
  text-align: center;
  font-size: 11px;
  color: #9d174d;
  opacity: 0.7;
}

.slide-down-enter-active,
.slide-down-enter-active {
  transition: opacity 0.22s ease, transform 0.22s ease, max-height 0.28s ease;
  max-height: 200px;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
  max-height: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
