<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="close">
      <div class="modal-container">

        <!-- Header -->
        <div class="modal-header">
          <div class="header-content">
            <h2 class="modal-title">{{ displayTitle }}</h2>
            <p v-if="displayConstraints" class="modal-subtitle">{{ displayConstraints }}</p>
          </div>
          <button class="close-btn" @click="close" title="Close (ESC)">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Progress -->
        <div v-if="state.running || state.report" class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <div class="progress-info">
            <span class="progress-stage">{{ progressStage }}</span>
            <span class="progress-percent">{{ Math.round(progressPercent) }}%</span>
          </div>
        </div>

        <!-- Main Content -->
        <div class="content-section">

          <!-- Tabs -->
          <div class="tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'research' }"
              @click="activeTab = 'research'"
            >
              🔬 Research
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'history' }"
              @click="switchToHistory"
            >
              📚 History ({{ historyRecords.length }})
            </button>
          </div>

          <!-- Research Tab -->
          <div v-show="activeTab === 'research'" class="tab-content">

            <!-- Input Form -->
            <div v-if="!state.running && !state.report" class="input-section">
              <div class="form-group">
                <label>Research Topic</label>
                <input
                  v-model="topic"
                  type="text"
                  placeholder="e.g., Applications of AI in healthcare"
                  @keyup.enter="handleStart"
                />
              </div>
              <div class="form-group">
                <label>Constraints (optional)</label>
                <textarea
                  v-model="constraints"
                  rows="3"
                  placeholder="Add specific requirements, e.g., focus on 2024 developments"
                ></textarea>
              </div>
              <div class="form-row">
                <div class="form-group half">
                  <label>Number of Tasks</label>
                  <select v-model="maxTasks">
                    <option :value="3">3 tasks</option>
                    <option :value="5">5 tasks</option>
                    <option :value="7">7 tasks</option>
                  </select>
                </div>
                <div class="form-group half">
                  <label>Category</label>
                  <select v-model="activeCategory">
                    <option value="research">General Research</option>
                    <option value="planning">Task Planning</option>
                    <option value="search">Multi-Source Search</option>
                    <option value="summarize">Deep Summarization</option>
                    <option value="report">Structured Reports</option>
                  </select>
                </div>
              </div>
              <button class="start-btn" @click="handleStart" :disabled="!topic.trim()">
                <span v-if="state.running" class="spinner"></span>
                <span>{{ state.running ? 'Researching...' : 'Start Research' }}</span>
              </button>
            </div>

            <!-- Loading State -->
            <div v-else-if="state.running && !state.report" class="loading-state">
              <div class="spinner-large"></div>
              <p class="loading-text">Conducting deep research, please wait...</p>
              <div class="log-container">
                <div v-for="(log, idx) in state.logs" :key="idx" class="log-item">
                  {{ log }}
                </div>
              </div>
            </div>

            <!-- Report Display -->
            <div v-else-if="state.report" class="report-section">
              <div class="report-actions">
                <button class="action-btn secondary" @click="reset">
                  🔄 New Research
                </button>
                <button v-if="viewingFromHistory" class="action-btn" @click="downloadReport">
                  📥 Download Report
                </button>
                <button v-else class="action-btn" @click="saveToHistory">
                  💾 Save to History
                </button>
              </div>
              <div class="markdown-content" v-html="renderedReport"></div>
            </div>

          </div>

          <!-- History Tab -->
          <div v-show="activeTab === 'history'" class="tab-content">
            <div class="history-header">
              <h3>📚 Research History</h3>
              <button class="refresh-btn" @click="loadHistory(activeCategory)">
                🔄 Refresh
              </button>
            </div>
            <div v-if="historyLoading" class="loading-msg">Loading...</div>
            <div v-else-if="!historyRecords.length" class="empty-msg">
              <div class="empty-icon">📭</div>
              <p>No history records yet</p>
            </div>
            <div v-else class="history-list">
              <div
                v-for="rec in historyRecords"
                :key="rec.id"
                class="history-item"
                :class="{ selected: selectedHistoryId === rec.id }"
                @click="loadHistoryItem(rec)"
              >
                <div class="history-title">{{ rec.topic }}</div>
                <div class="history-meta">
                  <span class="history-date">{{ formatDate(rec.created_at) }}</span>
                  <span class="history-category">{{ rec.category }}</span>
                </div>
                <button
                  class="delete-btn"
                  @click.stop="deleteHistory(rec.id)"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <span class="status-text">{{ statusText }}</span>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { marked } from 'marked'
import { useResearch } from '../composables/useResearch'
import { fetchHistory, deleteHistoryItem, saveManualHistory } from '../api/research'
import type { HistoryRecord, ResearchReport } from '../types/research'

const props = defineProps<{
  initialFeature?: string
  initialTab?: 'research' | 'history'
}>()

const emit = defineEmits<{
  close: []
  'research-complete': []
  'task-saved': []
}>()

const isOpen = ref(true)
const activeTab = ref(props.initialTab || 'research')
const activeCategory = ref(props.initialFeature || 'research')

// Research form
const topic = ref('')
const constraints = ref('')
const maxTasks = ref(5)

// History
const historyRecords = ref<HistoryRecord[]>([])
const historyLoading = ref(false)
const selectedHistoryId = ref<number | null>(null)
const viewingFromHistory = ref(false)

// Research state
const { state, start, reset: resetResearch, onResearchComplete, onTaskSaved } = useResearch()

function reset() {
  viewingFromHistory.value = false
  resetResearch()
}

// Display title: show fixed text while typing, real topic after research starts
const displayTitle = computed(() => {
  if (state.running || state.report) return topic.value || 'Deep Research'
  return 'Deep Research'
})

const displayConstraints = computed(() => {
  if (state.running || state.report) return constraints.value
  return ''
})

// Progress
const progressPercent = computed(() => {
  if (!state.running && state.report) return 100
  if (!state.running) return 0
  if (state.tasks.length === 0) return 10
  const completed = state.tasks.filter(t => t.status === 'completed').length
  return 10 + (completed / state.tasks.length) * 80
})

const progressStage = computed(() => {
  if (state.report) return 'Research Complete'
  if (!state.running) return 'Ready'
  if (state.tasks.length === 0) return 'Planning...'
  const pending = state.tasks.filter(t => t.status === 'pending').length
  const running = state.tasks.filter(t => t.status === 'running').length
  if (running > 0) return `Running: ${state.tasks.find(t => t.status === 'running')?.title}`
  if (pending === 0) return 'Generating report...'
  return `In Progress: ${state.tasks.length - pending}/${state.tasks.length}`
})

const statusText = computed(() => {
  if (state.error) return `Error: ${state.error}`
  if (state.report) return '✅ Research Complete'
  if (state.running) return '🔍 Researching...'
  return '⏸️ Ready'
})

// Report rendering — parse "Title||Content" sections
const renderedReport = computed(() => {
  if (!state.report) return ''
  const report = state.report

  const sectionsMd = (report.sections || []).map(section => {
    const sepIdx = section.indexOf('||')
    if (sepIdx === -1) return `## ${section}`
    const title = section.slice(0, sepIdx).trim()
    const content = section.slice(sepIdx + 2).trim()
    return `## ${title}\n\n${content}`
  }).join('\n\n')

  const refsMd = (report.references || []).length > 0
    ? `## References\n\n${report.references.map((r, i) => `${i + 1}. ${r}`).join('\n')}`
    : ''

  const markdown = `# ${report.title}

## Abstract
${report.abstract || ''}

${sectionsMd}

${refsMd}
`
  return marked(markdown)
})

// Methods
async function handleStart() {
  if (!topic.value.trim() || state.running) return
  viewingFromHistory.value = false
  await start(topic.value, constraints.value, maxTasks.value, activeCategory.value)
}

function close() {
  isOpen.value = false
  emit('close')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

async function switchToHistory() {
  activeTab.value = 'history'
  await loadHistory(activeCategory.value)
}

async function loadHistory(cat?: string) {
  historyLoading.value = true
  try {
    historyRecords.value = await fetchHistory(cat || undefined)
  } catch {
    // ignore
  } finally {
    historyLoading.value = false
  }
}

async function loadHistoryItem(rec: HistoryRecord) {
  selectedHistoryId.value = rec.id
  topic.value = rec.topic
  constraints.value = rec.constraints_ || ''
  state.report = JSON.parse(JSON.stringify(rec.report || {}))
  state.tasks = JSON.parse(JSON.stringify(rec.tasks || []))
  viewingFromHistory.value = true
  activeTab.value = 'research'
}

function downloadReport() {
  const report = state.report
  if (!report) return
  const sectionsMd = (report.sections || []).map((s: string) => {
    const i = s.indexOf('||')
    return i === -1 ? s : s.slice(0, i).trim() + '\n' + s.slice(i + 2).trim()
  }).join('\n\n')
  const content = `# ${report.title}

## Abstract
${report.abstract || ''}

${sectionsMd}

${report.references?.length ? `## References\n${report.references.map((r: string, i: number) => `${i + 1}. ${r}`).join('\n')}` : ''}
`
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${report.title || 'Research Report'}.md`
  a.click()
  URL.revokeObjectURL(url)
}

async function deleteHistory(id: number) {
  if (!confirm('Delete this record?')) return
  await deleteHistoryItem(id)
  await loadHistory(activeCategory.value)
}

async function saveToHistory() {
  if (!state.report) return
  try {
    await saveManualHistory(
      topic.value,
      constraints.value,
      activeCategory.value,
      state.report.references || [],
      state.tasks,
      state.report
    )
    alert('Saved to history!')
  } catch {
    alert('Save failed')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US')
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  if (props.initialTab === 'history') {
    loadHistory(activeCategory.value)
  }
  onResearchComplete(async () => {
    emit('research-complete')
    await loadHistory(activeCategory.value)
  })
  onTaskSaved(() => {
    emit('task-saved')
    loadHistory(activeCategory.value)
  })
})

watch(isOpen, (open) => {
  if (!open) {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000; padding: 20px;
}
.modal-container {
  width: 90vw; height: 90vh; max-width: 1200px;
  background: #fff; border-radius: 16px;
  box-shadow: 0 25px 80px rgba(0,0,0,0.3);
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 24px 32px; border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff;
}
.header-content { flex: 1; min-width: 0; }
.modal-title {
  font-size: 1.5rem; font-weight: 700; margin: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.modal-subtitle { font-size: 0.9rem; opacity: 0.9; margin: 8px 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.close-btn {
  background: rgba(255,255,255,0.2); border: none; color: #fff;
  width: 40px; height: 40px; border-radius: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s; margin-left: 16px;
}
.close-btn:hover { background: rgba(255,255,255,0.3); transform: scale(1.05); }

.progress-section { padding: 16px 32px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; }
.progress-bar { height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; transition: width 0.5s; }
.progress-info { display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem; color: #6b7280; }
.progress-stage { font-weight: 500; }
.progress-percent { font-weight: 600; color: #667eea; }

.content-section { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

.tabs { display: flex; gap: 8px; padding: 16px 32px 0; border-bottom: 1px solid #e5e7eb; background: #fff; }
.tab-btn {
  padding: 12px 24px; border: none; background: transparent; color: #6b7280;
  font-size: 0.95rem; font-weight: 500; cursor: pointer;
  border-bottom: 2px solid transparent; transition: all 0.2s;
}
.tab-btn:hover { color: #667eea; }
.tab-btn.active { color: #667eea; border-bottom-color: #667eea; }

.tab-content { flex: 1; overflow-y: auto; padding: 24px 32px; }

.input-section { max-width: 600px; margin: 0 auto; }
.form-group { margin-bottom: 20px; }
.form-group.half { flex: 1; }
.form-row { display: flex; gap: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #374151; font-size: 0.9rem; }
.form-group input, .form-group textarea, .form-group select {
  width: 100%; padding: 12px 16px; border: 1px solid #d1d5db;
  border-radius: 10px; font-size: 1rem; transition: all 0.2s; background: #fff;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}
.form-group textarea { resize: vertical; min-height: 80px; }
.start-btn {
  width: 100%; padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: 600;
  cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.start-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102,126,234,0.3); }
.start-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.loading-state { text-align: center; padding: 40px; }
.spinner-large {
  width: 60px; height: 60px; border: 4px solid #e5e7eb;
  border-top-color: #667eea; border-radius: 50%;
  animation: spin 1s linear infinite; margin: 0 auto 24px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 1.1rem; color: #6b7280; margin-bottom: 24px; }
.log-container {
  max-width: 600px; margin: 0 auto; text-align: left;
  background: #f9fafb; border-radius: 10px; padding: 16px; max-height: 200px; overflow-y: auto;
}
.log-item { font-size: 0.85rem; color: #4b5563; padding: 4px 0; border-bottom: 1px solid #e5e7eb; }
.log-item:last-child { border-bottom: none; }

.report-section { max-width: 800px; margin: 0 auto; }
.report-actions { display: flex; gap: 12px; margin-bottom: 24px; justify-content: center; }
.action-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
}
.action-btn.secondary { background: #f3f4f6; color: #374151; }
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

.markdown-content { line-height: 1.8; color: #1f2937; }
.markdown-content :deep(h1) { font-size: 1.8rem; color: #111827; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #e5e7eb; }
.markdown-content :deep(h2) { font-size: 1.4rem; color: #374151; margin-top: 32px; margin-bottom: 16px; }
.markdown-content :deep(p) { margin-bottom: 16px; }
.markdown-content :deep(ul), .markdown-content :deep(ol) { margin-bottom: 16px; padding-left: 24px; }
.markdown-content :deep(li) { margin-bottom: 8px; }
.markdown-content :deep(a) { color: #667eea; text-decoration: none; }
.markdown-content :deep(a:hover) { text-decoration: underline; }

.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.history-header h3 { font-size: 1.2rem; color: #374151; }
.refresh-btn { padding: 8px 16px; background: #f3f4f6; border: none; border-radius: 6px; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }
.refresh-btn:hover { background: #e5e7eb; }
.loading-msg, .empty-msg { text-align: center; padding: 60px 20px; color: #6b7280; }
.empty-icon { font-size: 4rem; margin-bottom: 16px; }
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item {
  display: flex; align-items: center; gap: 16px; padding: 16px 20px;
  background: #f9fafb; border-radius: 10px; cursor: pointer; transition: all 0.2s; border: 2px solid transparent;
}
.history-item:hover { background: #f3f4f6; border-color: #e5e7eb; }
.history-item.selected { border-color: #667eea; background: #eef2ff; }
.history-title { flex: 1; font-weight: 500; color: #374151; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-meta { display: flex; gap: 12px; font-size: 0.85rem; color: #6b7280; }
.history-category { background: #e0e7ff; color: #4f46e5; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; }
.delete-btn { background: none; border: none; cursor: pointer; opacity: 0.5; transition: opacity 0.2s; padding: 4px; }
.delete-btn:hover { opacity: 1; }

.modal-footer { padding: 16px 32px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center; }
.status-text { font-size: 0.9rem; color: #6b7280; font-weight: 500; }

@media (max-width: 768px) {
  .modal-overlay { padding: 0; }
  .modal-container { width: 100vw; height: 100vh; max-width: 100%; border-radius: 0; }
  .modal-header { padding: 16px 20px; }
  .modal-title { font-size: 1.2rem; }
  .tabs { padding: 12px 20px 0; }
  .tab-btn { padding: 10px 16px; font-size: 0.9rem; }
  .tab-content { padding: 20px; }
  .form-row { flex-direction: column; gap: 0; }
  .history-item { flex-direction: column; align-items: flex-start; gap: 8px; }
  .history-meta { width: 100%; justify-content: space-between; }
}
</style>
