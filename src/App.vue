<template>
  <div class="app">
    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">Deep Research Agent</span>
        </h1>
        <p class="hero-subtitle">
          Enter a research topic — AI handles planning, search, summarization, and report generation automatically
        </p>
        <button class="launch-btn" @click="openResearch()">
          <span class="btn-icon">🚀</span>
          <span>Start Research</span>
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
        <h3 class="card-title">{{ card.title }}</h3>
        <p class="card-desc">{{ card.desc }}</p>
        <div v-if="cardCounts[card.key] > 0" class="card-badge">
          {{ cardCounts[card.key] }} records
        </div>
      </div>
    </div>

    <ResearchModal
      v-if="showModal"
      :initial-feature="activeCategory"
      :initial-tab="activeTab"
      @close="showModal = false"
      @research-complete="refreshCounts"
      @task-saved="onTaskSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import ResearchModal from './components/ResearchModal.vue'

const showModal = ref(false)
const activeCategory = ref('')
const activeTab = ref<'research' | 'history'>('research')
const cardCounts = reactive<Record<string, number>>({})

const featureCards = [
  { key: 'research',  icon: '🔍', title: 'General Research',   desc: 'Deep research on any topic with structured report output' },
  { key: 'planning',  icon: '📋', title: 'Task Planning',      desc: 'View intelligent task decomposition and planning history' },
  { key: 'search',    icon: '🌐', title: 'Multi-Source Search', desc: 'Aggregated search results from multiple sources' },
  { key: 'summarize', icon: '📝', title: 'Deep Summarization', desc: 'Content summarization and key findings extraction' },
  { key: 'report',    icon: '📊', title: 'Structured Reports', desc: 'Complete research report generation history' },
  { key: 'sse',       icon: '⚡', title: 'Real-Time Tracking', desc: 'SSE streaming and execution log history' },
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
      const list = await fetchHistory(card.key, 1)
      cardCounts[card.key] = Array.isArray(list) ? list.length : 0
    } catch {
      cardCounts[card.key] = 0
    }
  }
}

async function onTaskSaved() {
  cardCounts['research'] = (cardCounts['research'] || 0) + 1
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
}
</style>
