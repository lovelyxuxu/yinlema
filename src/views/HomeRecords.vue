<script setup lang="ts">
const streakDays = 0;
</script>

<template>
  <div class="page">
    <header class="hero">
      <p class="eyebrow">自我管理</p>
      <h1>鹿了么</h1>
      <p class="lead">
        记录与统计功能将在这里展开：按天 / 周 / 月切换维度，并基于历史数据给出今日参考与鼓励文案。
      </p>
    </header>

    <section class="card">
      <p class="muted">当前占位</p>
      <p class="stat">你已经 <strong>{{ streakDays }}</strong> 天没鹿了</p>
      <p class="hint">后续可接入真实记录与图表。</p>
    </section>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 20px 16px 96px;
  max-width: 560px;
  margin: 0 auto;
}

.hero h1 {
  margin: 6px 0 10px;
  font-size: 28px;
  letter-spacing: 0.02em;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
  font-size: 14px;
}

.card {
  margin-top: 18px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--card-border);
}

.muted {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 13px;
}

.stat {
  margin: 0;
  font-size: 16px;
}

.stat strong {
  color: var(--accent-b);
  font-size: 20px;
}

.hint {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 13px;
}
</style>
