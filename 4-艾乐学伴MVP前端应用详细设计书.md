# 《艾乐学伴MVP前端应用详细设计书》

## 1. 概述

### 1.1 文档目的

本文档是艾乐学伴 MVP 1.0 H5 前端应用的完整工程实现指南。它定义了从项目搭建、技术选型到核心页面与组件实现细节的全过程，旨在确保前端开发团队高效、精准地构建与后端智能体服务对齐的用户界面。

### 1.2 设计对齐

- **产品与交互**：严格实现《前端界面原型与交互原型图》中定义的界面与交互。
- **数据契约**：严格遵循《API 接口规范全集（OpenAPI 3.0）》中定义的接口。
- **状态模型**：与《数据库详细设计书（DDL）》中的核心实体状态保持同步。
- **系统架构**：遵循《系统架构详细设计书》中定义的前后端通信模式。

## 2. 技术栈与项目结构

### 2.1 技术栈明细

| 类别        | 选型                           | 版本 | 用途说明                                  |
| ----------- | ------------------------------ | ---- | ----------------------------------------- |
| 框架        | React                          | 18+  | 构建组件化 UI，支持并发特性               |
| 语言        | TypeScript                     | 5.x  | 提供静态类型安全，与后端 API 类型严格对齐 |
| 构建工具    | Vite                           | 5.x  | 极速开发与构建                            |
| 路由        | React Router                   | 6.x  | 声明式路由，支持嵌套路由与数据加载        |
| 状态管理    | Zustand                        | 4.x  | 轻量灵活的全局状态管理                    |
| HTTP 客户端 | axios                          | 1.x  | 处理 REST API 调用                        |
| WebSocket   | 原生 WebSocket API             | -    | 处理实时消息（进度、介入、通知）          |
| UI 方案     | 自研组件 + Tailwind CSS        | 3.x  | 基于 Tailwind 工具类构建设计系统          |
| 拖拽库      | @dnd-kit                       | 6.x  | 支持“日清”计划调整等拖拽交互            |
| 图表库      | Recharts                       | 2.x  | 诊断报告等数据可视化                      |
| 音频处理    | Web Audio API /`<audio>`     | -    | 语音播放与录制                            |
| 测试框架    | Vitest + React Testing Library | -    | 单元与组件测试                            |
| 代码规范    | ESLint + Prettier              | -    | 代码质量与风格统一                        |

> 结论：文档已明确采用 **React 18 + TypeScript + Tailwind CSS** 技术方案。

### 2.2 项目目录结构

```text
src/
├── assets/                     # 静态资源
│   ├── images/
│   ├── fonts/
│   └── audios/                 # 占位或本地音频
├── components/                 # 可复用 UI 组件
│   ├── ui/                     # 基础组件 (Button, Input, Card, Dialog, Toast)
│   ├── layout/                 # 布局组件 (Header, Sidebar, AppShell)
│   ├── shared/                 # 业务通用组件
│   │   ├── TaskCard/
│   │   ├── ProblemSummaryCard/
│   │   ├── ContentPlayer/
│   │   ├── ConversationBubble/
│   │   └── PioppeIntervention/
│   └── journeys/               # 旅程专属组件
│       ├── DailyClearance/
│       └── TaskExecution/
├── containers/                 # 页面级容器组件（与路由一一对应）
│   ├── StartupSession/
│   ├── DailyClearance/
│   ├── TaskExecution/
│   ├── Diagnosis/
│   └── FreeChat/
├── hooks/                      # 自定义 React Hooks
│   ├── useWebSocket.ts
│   ├── useAudioRecorder.ts
│   ├── useApi.ts
│   ├── useAuth.ts
│   └── useJourneyState.ts
├── stores/                     # Zustand 全局状态
│   ├── useUserStore.ts
│   ├── useSessionStore.ts
│   ├── usePlanStore.ts
│   └── useContentStore.ts
├── services/                   # 后端 API 客户端
│   ├── apiClient.ts
│   ├── conversationService.ts
│   ├── planTaskService.ts
│   ├── contentService.ts
│   └── websocketService.ts
├── types/                      # TypeScript 类型定义
│   ├── api.ts
│   ├── domain.ts
│   └── ui.ts
├── utils/                      # 工具函数
│   ├── format.ts
│   └── validation.ts
├── config/                     # 应用配置
│   └── constants.ts
├── App.tsx                     # 应用根组件（路由配置）
├── main.tsx                    # 应用入口
└── index.css                   # 全局 Tailwind CSS
```

## 3. 全局状态管理设计

### 3.1 Zustand Store 结构

#### 1) `useUserStore`（用户信息）

```ts
interface UserState {
  user: Api.UserDetail | null;
  token: string | null;
  isAuthenticated: boolean;
  actions: {
    login: (phone: string, smsCode: string) => Promise<void>;
    logout: () => void;
    fetchProfile: () => Promise<void>;
  };
}
```

- 持久化：`token` 和 `user.id` 持久化到 `localStorage`。

#### 2) `useSessionStore`（会话与智能体上下文）

```ts
interface SessionState {
  currentJourney:
    | 'startup'
    | 'daily-clearance'
    | 'execution'
    | 'diagnosis'
    | 'free-chat'
    | null;
  sessionContext: Api.SessionContext | null; // PIOPPE 决策结果
  activeIntervention: Api.PioppeIntervention | null; // 当前活跃介入
  conversationHistory: Map<string, Message[]>; // key: journey_session_id
  actions: {
    fetchSessionContext: () => Promise<void>;
    clearActiveIntervention: () => void;
    respondToIntervention: (interventionId: string, optionId: string) => Promise<void>;
  };
}
```

#### 3) `usePlanStore`（学习计划与任务）

```ts
interface PlanState {
  currentPlan: Api.LearningPlan | null;
  tasks: Api.LearningTask[];
  focusedTask: Api.LearningTask | null;
  actions: {
    fetchCurrentPlan: () => Promise<void>;
    updateTaskStatus: (taskId: string, status: TaskStatusUpdateRequest) => Promise<void>;
    requestHelp: (taskId: string, diagnosis?: string) => Promise<void>;
  };
}
```

#### 4) `useContentStore`（内容生成与播放）

```ts
interface ContentState {
  generatingFor: { taskId: string; helpSessionId: string } | null;
  generationProgress: number; // 0-1

  currentPackage: Api.ContentPackage | null;
  playbackStatus: 'idle' | 'playing' | 'paused';

  actions: {
    fetchContentPackage: (packageId: string) => Promise<void>;
    sendFeedback: (packageId: string, feedbackType: 'NOT_UNDERSTAND') => Promise<void>;
  };
}
```

### 3.2 状态同步与副作用

- 启动时：恢复 `userStore` -> 获取 `sessionContext` -> 导航至对应旅程。
- WebSocket 消息：通过 `useWebSocket` 订阅消息并更新 store。
- `CONTENT_GENERATION_UPDATE` -> 更新 `useContentStore.generationProgress`。
- `PIOPPE_INTERVENTION` -> 更新 `useSessionStore.activeIntervention`。
- `CONTENT_PACKAGE_READY` -> 调用 `useContentStore.actions.fetchContentPackage`。

## 4. 核心组件实现详述

### 4.1 `<ContentPlayer />` 组件

- 用途：播放 AI 生成的多媒体内容包，是“创造”能力的呈现终端。

**Props**

```ts
interface ContentPlayerProps {
  packageId: string;
  autoPlay?: boolean;
  onEnded?: () => void;
  onNotUnderstand?: () => void;
}
```

**内部状态与逻辑（示例）**

```tsx
const ContentPlayer: React.FC<ContentPlayerProps> = ({
  packageId,
  autoPlay = true,
  onEnded,
  onNotUnderstand,
}) => {
  const { currentPackage, fetchContentPackage, generationProgress } = useContentStore();
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    fetchContentPackage(packageId);
  }, [packageId, fetchContentPackage]);

  const currentItem = currentPackage?.manifest[currentItemIndex];

  const handleNext = () => {
    if (!currentPackage) return;
    if (currentItemIndex < currentPackage.manifest.length - 1) {
      setCurrentItemIndex((prev) => prev + 1);
      return;
    }
    onEnded?.();
  };

  const handleNotUnderstand = () => {
    onNotUnderstand?.();
  };

  return (
    <div className="content-player">
      {!currentPackage && <div>加载中...</div>}

      {currentPackage?.status === 'generating' && (
        <div>生成中...{Math.round(generationProgress * 100)}%</div>
      )}

      {currentPackage?.status === 'ready' && currentItem && (
        <>
          {currentItem.type === 'text' && <div className="text-content">{currentItem.content}</div>}

          {currentItem.type === 'image' && (
            <div>
              <img src={currentItem.url} alt={currentItem.caption} />
              <p>{currentItem.caption}</p>
            </div>
          )}

          {currentItem.type === 'audio' && (
            <audio ref={audioRef} src={currentItem.url} autoPlay={autoPlay} onEnded={handleNext} controls />
          )}

          <div className="controls">
            <button onClick={() => audioRef.current?.pause()}>暂停</button>
            <button onClick={handleNotUnderstand}>没听懂</button>
            <button onClick={handleNext}>跳过</button>
          </div>
        </>
      )}
    </div>
  );
};
```

### 4.2 `<ConversationInterface />` 组件

- 用途：“日清”与“自由聊”旅程的核心对话界面，集成语音输入。
- 关键实现点：
- 语音录制：使用 `useAudioRecorder`，录制完成后上传获取 `audio_url`，与文本一并提交。
- 对话流渲染：使用 `useSessionStore.conversationHistory` 渲染当前旅程对话历史。
- 富媒体交互：气泡中的知识点标签和快捷按钮需绑定事件，触发知识卡片等动作。

## 5. 页面流与路由设计

### 5.1 路由配置（`App.tsx`）

```ts
const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />, // 包含导航栏等公共布局
    children: [
      { index: true, element: <NavigateToContext /> },
      { path: 'startup', element: <StartupSessionPage /> },
      { path: 'daily-clearance', element: <DailyClearancePage /> },
      { path: 'execution', element: <TaskExecutionPage /> },
      { path: 'diagnosis', element: <DiagnosisPage /> },
      { path: 'free-chat', element: <FreeChatPage /> },
    ],
  },
  { path: '/auth/login', element: <LoginPage /> },
]);
```

### 5.2 核心页面流

- 应用启动：
- `main.tsx` 检查 `useUserStore.isAuthenticated`。
- 已登录：调用 `useSessionStore.fetchSessionContext()`，再按结果导航。
- 未登录：导航至 `/auth/login`。
- 旅程一：日清（`DailyClearancePage`）
- 进入时：创建本地 `session_id`，调用 `POST /conversation/utterance` 发送初始问候。
- 对话中：用户输入 -> 调用接口 -> 更新本地历史 -> 渲染。
- 结束时：点击“我讲完了” -> 导航至 `/daily-clearance/resolutions`。
- 旅程二：执行（`TaskExecutionPage`）
- 布局：桌面端左学右练，移动端标签页；用 `usePlanStore.focusedTask` 管理聚焦任务。
- 求助流程：点击求助 -> `POST /tasks/{id}/help` -> 监听 `CONTENT_GENERATION_UPDATE` / `CONTENT_PACKAGE_READY` -> 渲染 `<ContentPlayer />`。

## 6. API 与 WebSocket 集成

### 6.1 服务层封装示例（`services/conversationService.ts`）

```ts
import apiClient from './apiClient';
import type {
  UnderstandRequest,
  UnderstandResponse,
  ClarifiedProblemInput,
  DailyClearanceResolutionsResponse,
} from '@/types/api';

export const conversationService = {
  async submitUtterance(data: UnderstandRequest): Promise<UnderstandResponse> {
    const response = await apiClient.post<UnderstandResponse>('/conversation/utterance', data);
    return response.data;
  },

  async getResolutions(
    sessionId: string,
    problems: ClarifiedProblemInput[],
  ): Promise<DailyClearanceResolutionsResponse> {
    const response = await apiClient.post('/daily-clearance/resolutions', {
      session_id: sessionId,
      clarified_problems: problems,
    });
    return response.data;
  },
};
```

### 6.2 WebSocket 集成（`hooks/useWebSocket.ts`）

```ts
const useWebSocket = (url: string) => {
  const ws = useRef<WebSocket | null>(null);
  const { token } = useUserStore();

  useEffect(() => {
    const connect = () => {
      const wsUrl = `${url}?token=${token}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket Connected');
      };

      ws.current.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        switch (message.type) {
          case 'CONTENT_GENERATION_UPDATE':
            useContentStore.getState().actions.updateGenerationProgress(message.data);
            break;
          case 'PIOPPE_INTERVENTION':
            useSessionStore.getState().actions.setActiveIntervention(message.data);
            break;
          default:
            break;
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket Disconnected');
        // TODO: 实现重连逻辑
      };
    };

    if (token) connect();
    return () => ws.current?.close();
  }, [url, token]);

  const sendMessage = (message: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { sendMessage };
};
```

## 7. 响应式与适配规范

### 7.1 断点定义（Tailwind CSS）

```js
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      sm: '640px',
      md: '768px', // 平板/桌面分界
      lg: '1024px',
      xl: '1280px',
    },
  },
};
```

### 7.2 布局策略

- 桌面/平板（`>= 768px`）：采用“主-次”面板布局。日清旅程为左对话右摘要，执行旅程为左学右练。
- 手机（`< 768px`）：采用垂直滚动布局，复杂功能（对话摘要、学伴面板）放入底部抽屉或标签页。

## 8. 测试策略

### 8.1 单元测试（Vitest）

- 目标：工具函数、自定义 Hooks、纯 UI 组件。
- 示例：测试 `useAudioRecorder` 的录制状态管理。

### 8.2 组件测试（React Testing Library）

- 目标：组件交互逻辑和条件渲染。
- 示例：测试 `<ContentPlayer />` 在不同 `status` 下的渲染，以及播放控制按钮点击行为。

### 8.3 端到端测试（Playwright）

- 目标：关键用户旅程的完整流程。
- 场景：用户登录 -> 进入日清 -> 语音提问 -> 获得解决方案 -> 加入计划 -> 开始执行 -> 求助 -> 播放讲解。

## 9. 部署与构建

- 环境变量：通过 `.env` 管理 API 基础 URL、WebSocket URL 等。
- Docker 化：提供 `Dockerfile` 进行容器化部署。
- 静态资源：构建产物为静态文件，可通过 Nginx 或 CDN 分发。

## 10. 总结与交付

本文档提供了从前端项目初始化到核心模块实现的完整蓝图，并与后端设计文档衔接。

基于此，前端团队可立即开展以下工作：

- 依据第 2 章搭建项目基础框架。
- 依据第 3 章实现全局状态管理。
- 依据第 4、5 章并行开发核心页面与组件。
- 依据第 6 章完成与后端服务的集成。
- 按第 7、8 章规范执行响应式适配与测试。

以上为《艾乐学伴 MVP 1.0 完整产品定义、架构与开发设计说明书（先进架构对齐终极版）》所规划的核心工程规格文档。
