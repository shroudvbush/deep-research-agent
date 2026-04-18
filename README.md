# 深度研究智能体 (Deep Research Agent)

基于 AI 的自动化深度研究助手，将任意研究主题通过智能任务规划、多源搜索、内容摘要、合成为结构化的研究报告。

> ⚠️ **系统要求：本项目仅支持 Windows 操作系统。**

## 功能特性

- **智能任务规划** — LLM 自动将研究主题分解为 3-7 个可执行的子任务
- **多源信息搜索** — 聚合多个网络来源的信息
- **实时进度追踪** — SSE 流式推送，实时展示研究进展
- **结构化报告** — 生成带分节、参考文献和核心发现的 Markdown 格式报告
- **历史记录管理** — SQLite 持久化存储，支持分类筛选和报告导出
- **卡片实时同步** — 每个子任务完成时，对应分类卡片计数即时更新

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | FastAPI (Python) |
| AI | OpenAI 兼容 API（DeepSeek V3 / GPT-4o 等） |
| 存储 | SQLite |
| 通信 | Server-Sent Events（SSE） |

## 项目架构

```
orchestrator.py ──► PlanningService ──► [Task 1] ──► SearchService ──► SummarizationService
                                   └─► [Task 2] ──► SearchService ──► SummarizationService
                                   └─► [Task N] ──► ... ──► ReportingService ──► Report
```

## 快速开始

### 1. 下载 & 安装

下载本项目后，**双击运行 `start.bat`**，脚本会自动完成以下操作：

- 检测并安装 Python 依赖（创建 venv）
- 检测并安装前端依赖（npm install）
- 启动后端服务（端口 8000）
- 启动前端服务（端口 3000）
- **自动打开浏览器**访问 http://localhost:3000

> 首次运行需要等待依赖安装（约 1-2 分钟），之后启动会更快。

### 2. 配置 API Key

项目根目录已有 `.env.example`，首次启动后：
1. 复制一份为 `.env`
2. 填入你的 LLM API Key：

```env
LLM_API_KEY=your_api_key_here（这里填写的是你自己的api密钥）
LLM_BASE_URL=https://api.siliconflow.cn/v1（由于演示用的是硅基流动里的deepseek模型，所以填写的是硅基流动的url，可按需更改）
LLM_MODEL=deepseek-ai/DeepSeek-V3-241206
SEARCH_PROVIDER=deepseek
```

> 无 API Key 时，系统会使用内置的演示模式（任务规划功能可用，其余功能受限）。

### 3. 开始使用

1. 打开 http://localhost:3000
2. 输入研究主题（如"人工智能在教育领域的应用"）
3. 可选填约束条件（如"聚焦 2024-2025 年最新发展"）
4. 选择任务数量（3/5/7 个子任务）
5. 点击 **开始研究**，等待报告生成

## 接口文档

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/research/stream` | POST | SSE 流式研究接口 |
| `/api/research/history` | GET | 获取研究历史列表 |
| `/api/research/history/{id}` | GET | 获取单条历史记录 |
| `/api/research/history/{id}` | DELETE | 删除历史记录 |
| `/api/health` | GET | 健康检查 |

### SSE 事件流

```
research_started → planning_started → planning_completed
→ task_started → task_completed (×N) → task_saved (×N)
→ report_started → report_completed → research_finished
```

## 项目目录结构

```
deep-research-agent/
├── app/                    # 后端应用
│   ├── api/                # API 路由
│   ├── core/               # 核心配置
│   ├── db/                 # 数据库操作
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   └── main.py             # FastAPI 入口
├── src/                    # 前端源码
│   ├── api/                # 前端 API 调用
│   ├── components/         # Vue 组件
│   ├── composables/       # Vue 组合式函数
│   ├── types/              # TypeScript 类型定义
│   ├── App.vue             # 主组件
│   └── main.ts             # 前端入口
├── index.html
├── package.json
├── requirements.txt       # Python 依赖
├── .env.example            # 环境变量示例
├── start.bat               # Windows 一键启动脚本
└── README.md
```

## 常见问题

**Q: 双击 start.bat 后窗口直接退出怎么办？**
> 以管理员权限运行 PowerShell，执行 `start.bat`，查看错误信息。

**Q: 提示 Python / Node.js 未找到？**
> 请先安装 [Python 3.8+](https://www.python.org/downloads/) 和 [Node.js 18+](https://nodejs.org/)。

**Q: 研究过程中报错？**
> 检查 `.env` 中的 API Key 是否正确，网络是否正常（部分搜索需要访问外网）。

## 开源许可

MIT
