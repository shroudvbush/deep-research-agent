export interface ResearchTask {
  id: string
  title: string
  goal: string
  priority: number
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export interface ResearchReport {
  title: string
  abstract: string
  sections: string[]
  references: string[]
}

export interface ResearchState {
  logs: string[]
  tasks: ResearchTask[]
  report: ResearchReport | null
  running: boolean
  error: string | null
}

export interface SSEEvent {
  event: string
  message: string
  payload?: {
    tasks?: ResearchTask[]
    task_id?: string
    sources?: string[]
    report?: ResearchReport
    id?: number
    stage?: string
    detail?: string
    error?: string
  }
}

export interface ResearchRequest {
  topic: string
  constraints: string
  max_tasks: number
  language: string
  category: string
}

export interface HistoryRecord {
  id: number
  created_at: string
  topic: string
  constraints_: string
  category: string
  sources: string[]
  tasks: ResearchTask[]
  report: ResearchReport
  status: string
}
