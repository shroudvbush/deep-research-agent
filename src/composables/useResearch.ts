import { reactive } from 'vue'
import { startResearchStream } from '../api/research'
import type { ResearchState, SSEEvent, ResearchReport, ResearchTask } from '../types/research'

export function useResearch() {
  const state = reactive<ResearchState>({
    logs: [],
    tasks: [],
    report: null,
    running: false,
    error: null,
  })

  let _onComplete: (() => void) | null = null
  let _onTaskSaved: (() => void) | null = null

  function addLog(msg: string) {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false })
    state.logs.push(`[${time}] ${msg}`)
  }

  function updateTaskStatus(taskId: string, status: ResearchTask['status']) {
    const t = state.tasks.find((t) => t.id === taskId)
    if (t) t.status = status
  }

  async function start(
    topic: string,
    constraints = '',
    maxTasks = 5,
    category = 'research',
    initialSources: string[] = [],
  ) {
    if (state.running) return
    state.running = true
    state.error = null
    state.logs = []
    state.tasks = []
    state.report = null
    addLog(`🚀 Starting: ${topic}`)

    await startResearchStream(
      topic,
      constraints,
      maxTasks,
      category,
      initialSources,
      (ev: SSEEvent) => {
        addLog(`[${ev.event}] ${ev.message}`)

        switch (ev.event) {
          case 'planning_completed':
            state.tasks = (ev.payload?.tasks ?? []).map((t: any) => ({
              ...t,
              status: 'pending',
            }))
            break
          case 'task_started':
            updateTaskStatus(ev.payload?.task_id, 'running')
            break
          case 'task_completed':
            updateTaskStatus(ev.payload?.task_id, 'completed')
            break
          case 'task_failed':
            updateTaskStatus(ev.payload?.task_id, 'failed')
            break
          case 'history_saved':
            _onComplete?.()
            break
          case 'report_completed':
            state.report = ev.payload?.report as ResearchReport
            break
          case 'research_finished':
            state.running = false
            addLog('✅ Research complete')
            _onComplete?.()
            break
          case 'error':
            state.error = ev.message
            state.running = false
            addLog(`❌ Error [${ev.payload?.stage ?? 'unknown'}]: ${ev.message}`)
            break
        }
      },
      (err: Error) => {
        state.error = err.message
        state.running = false
        addLog(`❌ Connection failed: ${err.message}`)
      }
    )
  }

  function reset() {
    state.logs = []
    state.tasks = []
    state.report = null
    state.running = false
    state.error = null
  }

  function onResearchComplete(cb: () => void) {
    _onComplete = cb
  }

  function onTaskSaved(cb: () => void) {
    _onTaskSaved = cb
  }

  return { state, start, reset, onResearchComplete, onTaskSaved }
}
