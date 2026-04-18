<template>
  <div class="app">
    <!-- Language Switch -->
    <div class="lang-switch">
      <button
        :class="{ active: locale === 'zh' }"
        @click="setLocale('zh')"
      >中文</button>
      <button
        :class="{ active: locale === 'en' }"
        @click="setLocale('en')"
      >EN</button>
    </div>

    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">{{ t('app.title') }}</span>
        </h1>
        <p class="hero-subtitle">{{ t('app.subtitle') }}</p>
        <button class="launch-btn" @click="openResearch()">
          <span class="btn-icon">🚀</span>
          <span>{{ t('app.start') }}</span>
        </button>
      </div>
    </div>

    <div class="features">
      <div
        v-for="card in featureCards"
        :key="card.key"
        class="card"
        @click="openResearch(card.key)"
      >
        <div class="card-icon">{{ card.icon }}</div>
        <h3 class="card-title">{{ t(card.titleKey) }}</h3>
        <p class="card-desc">{{ t(card.descKey) }}</p>
        <div v-if="cardCounts[card.key] > 0" class="card-badge">
          {{ cardCounts[card.key] }} {{ t('app.records') }}
        </div>
      </div>
    </div>

    <ResearchModal
      v-if="showModal"
      :initial-feature="activeCategory"
      :initial-tab="activeTab"
      @close="showModal = false"
      @research-complete="refreshCounts"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import ResearchModal from './components/ResearchModal.vue'
import { useI18n } from './i18n'

const { locale, setLocale, t } = useI18n()

const showModal = ref(false)
const activeCategory = ref('')
const activeTab = ref<'research' | 'history'>('research')
const cardCounts = reactive<Record<string, number>>({})

const featureCards = [
  { key: 'research',  icon: '🔍', titleKey: 'card.research.title',  descKey: 'card.research.desc' },
  { key: 'planning',  icon: '📋', titleKey: 'card.planning.title',  descKey: 'card.planning.desc' },
  { key: 'search',    icon: '🌐', titleKey: 'card.search.title',    descKey: 'card.search.desc' },
  { key: 'summarize', icon: '📝', titleKey: 'card.summarize.title', descKey: 'card.summarize.desc' },
  { key: 'report',    icon: '📊', titleKey: 'card.report.title',    descKey: 'card.report.desc' },
  { key: 'sse',       icon: '⚡', titleKey: 'card.sse.title',       descKey: 'card.sse.desc' },
]

async function openResearch(category = 'research') {
  activeCategory.value = category
  activeTab.value = category ? 'history' : 'research'
  showModal.value = true
}

async function refreshCounts() {
  for (const card of featureCards) {
    try {
      const { fetchHistory } = await import('./api/research')
      const list = await fetchHistory(card.key, 999)
      cardCounts[card.key] = Array.isArray(list) ? list.length : 0
    } catch {
      cardCounts[card.key] = 0
    }
  }
}

onMounted(refreshCounts)
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #fff;
  padding: 0 20px 60px;
  position: relative;
}

.lang-switch {
  position: absolute; top: 20px; right: 24px;
  display: flex; gap: 0; border-radius: 8px; overflow: hidden;
  border: 1px solid rgba(255,255,255,0.3); z-index: 10;
}
.lang-switch button {
  padding: 8px 16px; border: none; background: rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.7); font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.lang-switch button.active {
  background: rgba(255,255,255,0.3); color: #fff;
}
.lang-switch button:hover:not(.active) {
  background: rgba(255,255,255,0.2);
}

.hero { text-align: center; padding: 100px 20px 80px; }
.hero-content { max-width: 800px; margin: 0 auto; }
.hero-title { font-size: 3.5rem; font-weight: 800; margin-bottom: 20px; line-height: 1.2; }
.gradient-text {
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-subtitle { font-size: 1.25rem; opacity: 0.9; margin-bottom: 40px; line-height: 1.6; }
.launch-btn {
  display: inline-flex; align-items: center; gap: 12px;
  padding: 18px 48px; background: #fff; color: #4f46e5;
  border: none; border-radius: 50px; font-size: 1.1rem; font-weight: 700;
  cursor: pointer; box-shadow: 0 10px 40px rgba(0,0,0,0.2); transition: all 0.3s;
}
.launch-btn:hover { transform: translateY(-3px); box-shadow: 0 15px 50px rgba(0,0,0,0.3); }
.btn-icon { font-size: 1.3rem; }

.features {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px; max-width: 1200px; margin: 0 auto;
}
.card {
  background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2); border-radius: 20px;
  padding: 32px 24px; text-align: center; transition: all 0.3s;
  cursor: pointer; position: relative; overflow: hidden;
}
.card::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
  opacity: 0; transition: opacity 0.3s;
}
.card:hover { transform: translateY(-8px); background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.3); box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.card:hover::before { opacity: 1; }
.card-icon { font-size: 3rem; margin-bottom: 16px; }
.card-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 12px; color: #fff; }
.card-desc { font-size: 0.95rem; opacity: 0.8; line-height: 1.6; }
.card-badge {
  margin-top: 16px; font-size: 0.8rem; background: rgba(79,70,229,0.6);
  border-radius: 20px; padding: 6px 16px; display: inline-block; font-weight: 500;
}

@media (max-width: 768px) {
  .hero { padding: 60px 20px 50px; }
  .hero-title { font-size: 2.5rem; }
  .hero-subtitle { font-size: 1.1rem; }
  .launch-btn { padding: 16px 36px; font-size: 1rem; }
  .features { grid-template-columns: 1fr; gap: 16px; }
  .card { padding: 24px 20px; }
  .lang-switch { top: 12px; right: 12px; }
  .lang-switch button { padding: 6px 12px; font-size: 0.8rem; }
}
</style>
