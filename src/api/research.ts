import type { SSEEvent, ResearchRequest, HistoryRecord } from '../types/research'

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8000'

export async function startResearchStream(
  topic: string,
  constraints: string,
  maxTasks: number,
  category: string,
  onEvent: (event: SSEEvent) => void,
  onError: (err: Error) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/research/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic,
      constraints,
      max_tasks: maxTasks,
      language: 'zh-CN',
      category,
    } as ResearchRequest & { category: string }),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`HTTP ${response.status}: ${detail}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6)) as SSEEvent
            onEvent(data)
          } catch {
            console.warn('[research.ts] Malformed SSE line:', line)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

export async function fetchHistory(category?: string, limit = 20): Promise<HistoryRecord[]> {
  const cat = category ? `?category=${encodeURIComponent(category)}` : ''
  const res = await fetch(`${API_BASE}/api/research/history${cat}&limit=${limit}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchHistoryItem(id: number): Promise<HistoryRecord> {
  const res = await fetch(`${API_BASE}/api/research/history/${id}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function deleteHistoryItem(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/research/history/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}

export async function saveManualHistory(
  topic: string,
  constraints: string,
  category: string,
  sources: string[],
  tasks: unknown[],
  report: unknown
): Promise<number> {
  const res = await fetch(`${API_BASE}/api/research/history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, constraints, category, sources, tasks, report }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  return data.id
}
