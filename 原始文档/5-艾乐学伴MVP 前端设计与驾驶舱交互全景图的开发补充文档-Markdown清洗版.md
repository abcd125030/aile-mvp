艾乐学伴MVP前端设计与驾驶舱交互全景图的

开发补充文档

仔细阅分析两份详细前端设计文档《L2：前端核心组件逻辑与状态流转图》和《L3：前端核心界面布局与硬件适配规范图》， 总体评价是：这两份文档质量非常高，已经超出了普通MVP设计的细致程度。 它们共同构建了一个清晰、模块化且具有前瞻性的前端架构，完全符合“学习驾驶舱”和“个人智能学伴”的战略定位。开发团队完全可以依据此进行技术选型和初期开发。

以下是详细评估，围绕所提出的四个问题展开：

### 一、是否符合战略定位？

完全符合，且在多个维度上进行了出色的落地演绎。

- “学习驾驶舱”/多线程工作模式 ：

- L3.2/L3.3的“三栏/全屏-面板”布局 ：完美支持“左边看任务清单，中间做题，右边看提示/讲解”的核心场景，实现了信息的并行处理和自由切换。

- L2.2/L3.6的画中画播放器 ：这是“持续任务”模式的精髓。允许讲解视频浮动、可缩放、持续播放，使用户在切换任务（如从任务A到任务B）时，讲解不中断，真正实现了“一心多用”的驾驶舱体验。

- L2.3/L3.7的临现工具面板 ：实现了“工具临现，用完即走”的理念。面板从侧边或底部呼出，不侵占主任务空间，是驾驶舱中灵活调用工具台的典范。

- “个人智能学伴”（PIOPPE）的融入 ：

- L2.4的规则引擎与L2.6/L3.9的介入组件 ：构成了PIOPPE的“感知-决策-触达”闭环。规则引擎基于全局状态做出决策，再通过气泡/卡片等非侵入式组件进行轻度干预，这与“智能学伴”的辅助定位高度一致。

- 融入核心旅程 ：在“任务执行”中求助时触发内容生成（L1.2），在“自由聊”中提供建议气泡（L3.5），在“诊断报告”中提供动态建议（L3.4），PIOPPE无处不在，但又不喧宾夺主。

- “探索-训练-诊断”核心循环 ：

- L1的三段式旅程设计清晰地刻画了这一循环。状态机（L1.x-Sx.x.x）明确展示了用户在三个核心模式间的流转路径，界面布局（L3）则为每个阶段提供了最优化的工作界面。

### 二、是否全面、详细，能够给到开发团队照着开发？

非常全面和详细，是优秀的开发指导文档。 特别是以下几点：

- 架构清晰，模块解耦 ：L2文档将系统分解为8个核心组件，并明确定义了每个组件的状态机（State Machine）。这种基于状态的设计思想是现代前端框架（如React, Vue）的最佳实践，极大降低了开发复杂度和维护成本。

- 交互逻辑与UI规范分离 ：L2定义“行为”（状态流转、事件响应），L3定义“表现”（布局、样式、动效）。这种分离让开发和设计可以并行工作，也有利于后续的替换与迭代。

- 细节丰富 ：

- 状态穷举 ：每个组件的状态机几乎涵盖了所有可能情况（如播放器的加载、播放、暂停、错误、结束）。

- 硬件适配具体 ：L3文档为桌面、移动、大屏等不同设备提供了精确的像素级布局、交互规则（如拖拽、手势、遥控器导航）和适配逻辑（如移动端强制bottom锚点）。

- 规则明确 ：文档中包含了大量明确的规则，例如“成功通知5秒后自动消失，除非悬停”、“同一时间只应显示一个全局通知条”等，减少了开发中的歧义。

开发团队可以据此 ：1）进行技术架构设计；2）编写组件的公共状态管理（如使用Zustand, Redux）；3）实现每个基础组件（`<ContentPlayer>`, `<GlobalNotification>`等）；4）搭建响应式布局框架；5）实现主要的页面路由与组合。

### 三、有哪些遗漏点、设计不合理之处、未满足战略定位之处？

尽管文档非常出色，但在“照着开发”的极致要求下，仍有一些可以补充和优化的地方：

#### 【遗漏点】

- 全局状态（Global Store）的数据结构定义缺失 ：

文档频繁提到plan.focusedTask、ui.globalPanels等全局状态，但 没有一份集中的、类型化的全局状态树定义 。开发时这会成为关键瓶颈。需要补充类似下面的定义：

```typescript
interface AppState {

```
user: User;

plan: {

focusedTask: Task | null;

taskList: Task[];

```typescript
// ... 其他学习计划相关状态

};

```
ui: {

globalPanels: Array<{id: string, anchor: ‘left’|’right’|’bottom’, contentType: string, props: object}>;

notification: Notification | null;

```typescript
// ... 其他UI控制状态

};

```
piopee: {

```typescript
// PIOPPE引擎的运行时状态

};

}

```
- 组件间的数据流与通信机制描述不足 ：

- L2文档描述了组件内部的状态流转，但 组件之间如何交互 ？例如，`<ContentPlayer>`播放完毕如何触发`<GlobalNotification>`显示？PIOPPERulesEngine的决策如何传递到`<PioppeIntervention>`组件？

- 需要补充一张 高层级的数据流图 ，说明核心状态（如plan，ui）如何通过Props/Context/Event Bus流向各组件，以及组件发出的事件如何更新全局状态。

- 错误边界与加载状态 ：

- 文档强调了成功和进行中的状态，但对于网络异常、接口失败、资源加载超时等错误情况的UI处理较为笼统。除了`<GlobalNotification>`的失败状态，每个组件（如`<ContentPlayer>`，临现面板）自身的错误回退UI（如展示重试按钮的占位图）需要更细化的规范。

- “加载中”的状态设计可以更丰富。例如，列表的骨架屏（Skeleton）、按钮的加载状态等。

- 无障碍访问（A11y）考虑 ：

- 作为教育产品，应服务所有学生。文档中缺乏对无障碍访问的说明，例如：

- 组件的ARIA标签（aria-label，role）。

- 键盘导航顺序（特别是在诊断报告的焦点联动、临现工具面板中）。

- 屏幕阅读器对于动态内容（如通知条、PIOPPE气泡）的播报策略。

- 深色模式/主题化 ：

- 文档中提到了颜色（如通知条的成功绿、警告黄），但没有形成完整的 设计令牌（Design Tokens）系统 （如--color-primary，--spacing-unit）。这不利于主题切换和保持视觉一致性。

#### 【设计不合理或可优化之处】

- L3.2 桌面端“任务执行”布局的潜在问题 ：

- 右侧面板默认显示“任务提示”，点击“求助”后变为“生成中”并最终变为“播放器”。这里的 状态切换逻辑略显生硬 。当播放器以画中画形式浮动后，右侧面板应该显示什么？变回“任务提示”，还是显示“讲解文本概要”？需要明确规则。建议：播放器浮出后，右侧面板可显示该讲解的 文字稿或关键步骤 ，作为辅助参考，这更符合“驾驶舱”多信息并行的理念。

- L2.5 全局通知的生命周期管理 ：

- 规则“同一时间只应显示一个全局通知条”是好的，但 “新通知到达时，如果当前有通知正在显示，应根据优先级决定...”  这条规则过于模糊。需要明确定义优先级（例如：错误 >成功 >加载）。并且， 加载中的通知 （如“内容生成中”）是否可被更高优先级的通知打断？如果被打断，后台任务是否继续？用户如何知晓？这里需要更严谨的设计。

- L3.9 PIOPPE介入的触发防抖 ：

- PIOPPE介入虽然智能，但频繁触发（例如在用户快速打字或频繁切换任务时）可能造成干扰。需要在L2.4的规则引擎中或L2.6的组件触发层加入 防抖（Debounce）或节流（Throttle）机制 ，以及基于会话的介入频率限制。

- 移动端适配的细节 ：

- L3.3移动端“帮助视图” ：描述为“全屏”，但从“任务专注视图”进入时，顶部导航栏的文字从“<返回”变成了“<返回讲解”，这个变化很精妙，但文档未明确其动画效果（是简单的替换，还是带有滑动的转场？）。

- 虚拟键盘处理 ：虽然提到了输入框聚焦时底部栏调整，但未提及在“自由聊”（L3.5）等全屏输入场景中，虚拟键盘弹出对整体布局（特别是对话框和PIOPPE气泡位置）的影响，需要有应对策略。

#### 【对战略定位的潜在不足】

- “个性化”的深度体现不足 ：当前设计完美体现了“实时辅助”的个性化（如根据当前焦点任务提供讲解）。但对于 长期个性化 （如根据历史错题、学习风格动态调整“探索”页内容推荐、任务难度）在UI层体现不足。`<PlanNavigator>`组件目前更像一个静态列表，未来可考虑加入“推荐星级”、“预测难度”等个性化标签。

- “社交”或“对比”维度缺失 ：战略定位中提到“学伴”，目前PIOPPE是AI学伴。是否未来有引入“同伴”学习的计划？UI上没有预留入口或展示位置（如“同学们常在这里遇到困难”）。这并非当前MVP的必须项，但值得思考。

### 四、其他建议

- 补充一份“组件交互关系图” ：在L2和L3之间，可以增加一张图，展示8个核心组件在几个主要页面（探索、任务执行、诊断、自由聊）中是如何被组合使用的，以及它们之间通过全局状态和事件的总线关系。

- 定义更详细的响应式断点（Breakpoints） ：L3区分了桌面、平板、手机，但实际开发需要具体的像素断点（例如：<768px手机，768px~1024px平板，>1024px桌面）。不同布局变化的精确断点需要明确。

- 动效参数具体化 ：文档提到了“滑入300ms”、“淡入200ms”等，非常好。可以统一整理一份 动效令牌表 ，包含缓动函数（ease-in-out）、持续时间等，确保体验一致。

- 图标与插图规范 ：文档中用了很多占位图标（[���]， [���]）。需要一份图标库列表或插图使用规范，确保视觉统一。

- 测试用例场景建议 ：可以基于这些状态机和交互规则，初步推导出一些关键的端到端（E2E）测试场景，对开发和质量保障团队非常有帮助。例如：“在桌面端任务执行页面，播放画中画讲解，然后切换到另一个任务，验证讲解是否继续浮动播放”。

### 总结

所提供的这两份文档 已经构成了一个坚实、详尽、高水准的MVP前端设计蓝图 ，战略定位得到精准贯彻，细节足以支撑开发启动。

主要优势在于：清晰的组件化架构、基于状态机的严谨逻辑、覆盖多端且细致的交互规则，以及将PIOPPE深度融入用户体验的设计。

为了达到“照着开发”的终极目标，建议按优先级补充以下内容 ：

1. （高）定义清晰的全局状态树（TypeScript接口） 。
2. （高）绘制组件间数据流与事件通信图 。
3. （中）补充关键组件的极端状态（错误、空状态）UI和响应式断点具体值 。
4. （中）细化移动端复杂交互（如转场动画、虚拟键盘处理）和通知优先级规则 。
5. （低）考虑无障碍访问和深色模式的设计令牌 。

完成这些补充后，这份文档将无可挑剔，能极大提升开发效率并确保产品最终体验与设计初衷高度一致。

基于对现有文档的评估，要达成“开发团队能无需深度思考即能对照开发”的目标，我们需要在现有优秀的L1、L2、L3文档基础上，进行系统性增补。

为此，策划输出以下四份增量文档，它们将分别解决数据结构、设计修正、基础规范和质量验证四个层面的问题：

1. 《L0：应用全局状态与数据流定义》

- 目的 ：弥补最根本的遗漏——定义整个应用唯一可信的数据源（Single Source of Truth）及其流动规则。这是所有组件交互的基石。

- 核心内容 ：

- 全局状态树（Global Store）TypeScript 接口定义 ：明确定义user, plan, ui, conversation, piopee等核心模块的完整数据结构。

- 组件-状态关系图 ：一张高层图表，清晰展示各核心组件（L2所定义）如何读写全局状态的特定部分，以及组件间如何通过状态和事件进行通信。

- 关键数据流描述 ：对几个核心交互（如“点击求助并播放内容”、“PIOPPE触发介入”、“完成诊断并查看报告”）的数据变更路径进行逐步说明。

2. 《L1/L2/L3 设计优化与细则增补（V1.1）》

- 目的 ：直接回应并修正之前分析中指出的所有“设计不合理或可优化之处”，将优化方案转化为可执行的开发规则。

- 核心内容 ：

- 任务执行旅程优化 ：明确“求助”后右侧面板的状态切换逻辑（如：播放器浮出后，面板显示讲解文稿）。

- 全局通知优先级规则 ：明确定义错误> 成功 > 加载中的优先级，及打断、排队的具体行为逻辑。

- PIOPPE触发防抖与频率限制规则 ：为L2.4规则引擎补充防止干扰的具体参数（如：同一会话中，同类型介入至少间隔30秒）。

- 移动端交互细则 ：明确“帮助视图”转场动画、虚拟键盘弹出时各界面元素的响应式行为规则。

- 响应式断点明确定义 ：给出具体的像素断点（如：手机: <768px, 平板: 768~1024px, 桌面: >1024px）。

3. 《L4：设计令牌与无障碍访问（A11y）规范》

- 目的 ：建立视觉与交互一致性的底层系统，并补全产品包容性的关键要求。

- 核心内容 ：

- 设计令牌（Design Tokens）表 ：定义色彩、字体、间距、圆角、阴影、动效时长与缓动函数的CSS/SCSS变量名及具体值。

- 组件状态颜色映射 ：将L3.8（通知条）、L3.9（介入组件）等处的状态色值关联到设计令牌。

- 无障碍访问（A11y）规范 ：为每个核心组件定义必要的ARIA标签、键盘导航顺序、焦点管理规则，以及动态内容（如通知、PIOPPE气泡）的屏幕阅读器播报策略。

4. 《核心组件交互测试场景（供QA参考）》

- 目的 ：基于复杂的状态机与交互规则，推导出关键的用户旅程测试用例，为质量保障团队提供验证蓝图，反向确保开发实现符合设计意图。

- 核心内容 ：

- 端到端（E2E）测试场景列表 ：例如“在桌面端任务执行页面，播放画中画讲解，然后切换到探索页，验证讲解是否持续浮动播放并始终位于顶层”。

- 状态机覆盖用例 ：针对L2中每个组件的状态机，设计触发各状态流转的关键操作步骤。

- 跨设备兼容性测试要点 ：强调在桌面、移动、大屏设备上需特别验证的交互点（如移动端手势、大屏端遥控器导航）。

# L0：应用全局状态与数据流定义

## 1. 文档说明

目的 ：本文档定义了艾乐学伴Web/移动端应用前端的全局状态树（Global Store）数据结构与 核心数据流规则 。它是L1、L2、L3层设计实现的 数据基石 ，确保所有组件拥有一致、可预测的数据源。

上级链接 ：本文档是L1（旅程状态）、L2（组件逻辑）、L3（界面布局）所有设计与交互的 底层数据模型 。开发团队应基于此定义来构建应用的状态管理（如使用Redux, Zustand, Pinia等）。

核心价值 ：

- 单一数据源 ：明确定义整个应用的状态全貌，消除歧义。

- 类型安全 ：提供完整的TypeScript接口定义，用于开发时静态类型检查。

- 数据流可追溯 ：描绘状态如何在不同组件和模块间流动，使复杂交互逻辑清晰可控。

## 2. 全局状态树（Global Store）

以下为应用核心状态的完整TypeScript接口定义。

```typescript
// ==================== 核心领域模型 ====================interface User {

```
id: string;

name: string;

avatar?: string;

```typescript
// ... 其他用户属性

}

interface KnowledgePoint {

```
id: string;

title: string;

description?: string;

mastery?: number; // 掌握度 0-1

```typescript
}

interface Task {

```
id: string;

title: string;

type: 'explore' | 'practice' | 'test'; // 对应探索、训练、诊断

status: 'pending' | 'active' | 'completed';

associatedKnowledgePoints: KnowledgePoint[];

```typescript
// ... 其他任务属性

}

interface DiagnosisItem {

```
id: string;

title: string;

description: string;

confidence: number; // 置信度 0-1

relatedTaskId?: string; // 可关联回具体任务

```typescript
}

interface Content {

```
id: string;

type: 'video' | 'audio' | 'text' | 'animation';

title: string;

url: string;

transcript?: string; // 文字稿（用于辅助功能及右侧面板显示）

duration?: number; // 时长（秒）

```typescript
}

interface ConversationMessage {

```
id: string;

role: 'user' | 'assistant';

content: string;

timestamp: number;

attachments?: Array<{type: string; url: string}>;

```typescript
}

// ==================== 应用全局状态接口 ====================interface AppState {

// ----- 用户与身份 -----

```
user: User | null;

auth: {

isAuthenticated: boolean;

token?: string;

```typescript
};

// ----- 学习规划与进展 -----

```
plan: {

```typescript
// 当前聚焦的任务（用户正在处理的核心任务）

```
focusedTask: Task | null;

```typescript
// 当前旅程模式：对应L1的三大旅程

```
currentJourney: 'explore' | 'practice' | 'diagnose' | 'free_chat';

```typescript
// 当前旅程下的任务列表（如探索列表、训练计划、诊断历史）

```
taskList: Task[];

```typescript
// 知识图谱/知识库快照

```
knowledgeGraph: KnowledgePoint[];

```typescript
};

// ----- 内容与会话 -----

```
content: {

```typescript
// 当前正在播放或生成的内容

```
currentPlaying: {

contentId: string | null;

associatedTaskId: string | null; // 内容关联的任务（如有）

state: 'idle' | 'buffering' | 'playing' | 'paused' | 'error'; // 对应L2.2

```typescript
};

// 内容播放队列（用于连续播放）

```
playQueue: Content[];

```typescript
};

```
conversation: {

```typescript
// 当前自由对话的会话ID

```
currentSessionId: string | null;

```typescript
// 当前会话的消息历史

```
messages: ConversationMessage[];

```typescript
// 语音输入状态

```
isRecording: boolean;

```typescript
};

// ----- 诊断报告 -----

```
diagnosis: {

```typescript
// 最新或当前查看的诊断报告

```
currentReport: {

id: string | null;

items: DiagnosisItem[];

overallScore?: number;

generatedAt?: number;

```typescript
} | null;

// 诊断详情当前聚焦的条目ID（用于与建议联动）

```
focusedDiagnosisItemId: string | null;

```typescript
};

// ----- 用户界面状态 -----

```
ui: {

```typescript
// 全局临现工具面板 (对应L2.3)

```
globalPanels: Array<{

id: string;

anchor: 'left' | 'right' | 'bottom';

contentType: 'task_hint' | 'content_transcript' | 'knowledge_detail' | 'diagnosis_detail' | 'note_editor';

contentProps: any; // 传递给面板组件的属性

isOpen: boolean;

```typescript
}>;

// 全局异步任务通知 (对应L2.5)

```
notification: {

id: string;

type: 'loading' | 'success' | 'error' | 'info';

title: string;

description?: string;

progress?: number; // 0-1

action?: { label: string; callback: () => void };

autoDismissDelay?: number; // 自动消失延迟(ms)

```typescript
} | null;

// 画中画播放器状态 (部分与content.currentPlaying重叠，但包含UI状态)

```
pictureInPicturePlayer: {

isVisible: boolean;

position: { x: number; y: number }; // 桌面端坐标

size: { width: number; height: number }; // 桌面端尺寸

mode: 'docked' | 'floating' | 'fullscreen'; // 对应L2.2的UI状态

```typescript
};

// PIOPPE轻度介入 (对应L2.6)

```
piopeeIntervention: {

isVisible: boolean;

type: 'suggestion' | 'reminder';

title: string;

description: string;

actions: Array<{ label: string; callback: () => void }>;

timeout: number; // 自动消失时间

```typescript
} | null;

// 其他全局UI状态

```
theme: 'light' | 'dark';

sidebarCollapsed: boolean; // 左侧栏是否折叠（桌面端）

```typescript
};

// ----- PIOPPE引擎运行时状态 -----

```
piopee: {

```typescript
// 最近一次介入的上下文

```
lastInterventionContext: any;

```typescript
// 介入频率限制器（用于防抖）

```
interventionCooldown: Record<string, number>; // key为介入类型，值为上次触发时间戳

```typescript
};

// ----- 系统状态 -----

```
system: {

networkStatus: 'online' | 'offline';

activeViewport: 'desktop' | 'tablet' | 'mobile' | 'tv'; // 当前视窗类型

```typescript
};

}

```
## 3. 组件-状态关系图

下图描绘了核心组件（L2定义）如何与全局状态树（L0定义）进行交互。箭头方向代表“读取”或“写入”关系。

```mermaid
graph TD

subgraph “全局状态树 AppState”

A1[plan.focusedTask]

A2[content.currentPlaying]

A3[ui.globalPanels]

A4[ui.notification]

A5[ui.pictureInPicturePlayer]

A6[ui.piopeeIntervention]

A7[diagnosis.currentReport]

A8[diagnosis.focusedDiagnosisItemId]

end

subgraph “核心组件 L2”

B1[“PlanNavigator (L2.1)”]

B2[“ContentPlayer (L2.2)”]

B3[“GlobalPanel (L2.3)”]

B4[“PIOPPERulesEngine (L2.4)”]

B5[“GlobalNotification (L2.5)”]

B6[“PioppeIntervention (L2.6)”]

B7[“DiagnosisReport (L2.7)”]

B8[“FreeChat (L2.8)”]

end

%% 读取关系

B1 -- “读取/写入” --> A1

B2 -- “读取/写入” --> A2

B2 -- “读取/写入” --> A5

B3 -- “读取” --> A3

B4 -- “读取” --> A1

B4 -- “读取” --> A2

B4 -- “读取” --> A7

B5 -- “读取” --> A4

B6 -- “读取” --> A6

B7 -- “读取” --> A7

B7 -- “读取/写入” --> A8

B8 -- “读取/写入” --> A2

%% 写入/触发关系

B4 -- “触发显示” --> A6

B4 -- “触发显示” --> A4

B3 -- “触发打开/关闭” --> A3

B5 -- “触发显示/关闭” --> A4

B6 -- “触发显示/关闭” --> A6

```
关系解读 ：

PlanNavigator (L2.1) ：读取并设置plan.focusedTask。当用户点击一个任务时，更新此状态，这将驱动主内容区（L3.2/L3.3）和PIOPPE引擎。

ContentPlayer (L2.2) ：读取content.currentPlaying以获取播放内容与状态，并写入该状态（如播放、暂停）。同时，其UI形态（画中画）由 ui.pictureInPicturePlayer控制。

GlobalPanel (L2.3) ：是一个“哑组件”，其显示内容完全由 ui.globalPanels数组驱动。其他组件通过更新此状态数组来打开/关闭面板。

PIOPPERulesEngine (L2.4) ：是 状态监听与决策中枢 。它持续监听plan, content, diagnosis等状态的变化，根据规则逻辑，决定是否触发通知(ui.notification) 或介入 (ui.piopeeIntervention)。

GlobalNotification(L2.5) & PioppeIntervention (L2.6) ：是“呈现组件”，它们只负责将 ui.notification和ui.piopeeIntervention的状态渲染到屏幕上。它们自身不改变这些状态，关闭或操作由触发它们的引擎或其他逻辑处理。

DiagnosisReport (L2.7) ：读取diagnosis.currentReport显示报告，并管理diagnosis.focusedDiagnosisItemId。当用户点击某个诊断条目时，更新此ID，这将联动影响“建议”部分（逻辑在L2.4中）。

FreeChat (L2.8) ：管理conversation.messages和conversation.isRecording。在特定情况下（如用户请求讲解），可触发设置content.currentPlaying状态。

## 4. 关键数据流场景示例

以下描述几个核心交互的完整数据状态变更路径。

### 场景一：用户在“任务执行”旅程中点击“求助”按钮

用户操作 ：在任务执行界面（L3.2）点击“求助”按钮。

事件触发 ：按钮点击事件被触发，携带当前plan.focusedTask.id。

状态变更1 (UI) ：

```typescript
// ui.globalPanels 被更新

ui.globalPanels.push({

```
id: 'help_panel',

anchor: 'right',

contentType: 'content_transcript', // 先显示“生成中”或占位符

contentProps: { taskId: plan.focusedTask.id },

isOpen: true

```typescript
});

```
状态变更2 (通知) ：

```typescript
// ui.notification 被更新

ui.notification = {

```
type: 'loading',

title: '正在生成讲解内容',

progress: 0

```typescript
};

```
异步请求 ：向后端发起内容生成请求。

异步响应 ：收到后端响应，包含生成的内容数据contentData。

状态变更3 (内容) ：

```typescript
// content.currentPlaying 被更新

content.currentPlaying = {

```
contentId: contentData.id,

associatedTaskId: plan.focusedTask.id,

state: 'buffering'

```typescript
};// 播放器开始缓冲

```
状态变更4 (面板内容更新) ：

```typescript
// 找到刚才打开的面板，更新其内容类型和属性const panel = ui.globalPanels.find(p => p.id === 'help_panel');if (panel) {

```
panel.contentType = 'content_transcript';

panel.contentProps = { content: contentData };

```typescript
}

```
状态变更5 (通知更新) ：

```typescript
ui.notification = {

```
type: 'success',

title: '讲解内容已就绪',

action: { label: '播放', callback: () => { /* 触发播放 */ } }

```typescript
};

```
UI渲染 ：GlobalPanel组件根据新的contentType和contentProps渲染讲解文稿。ContentPlayer组件根据content.currentPlaying.state进入播放状态。GlobalNotification显示成功提示。

### 场景二：PIOPPE引擎触发“诊断后建议”介入

状态监听 ：PIOPPERulesEngine监听diagnosis.focusedDiagnosisItemId的变化。

规则匹配 ：当diagnosis.currentReport存在且diagnosis.focusedDiagnosisItemId发生变化（用户点击了某个诊断条目）时，规则引擎被触发。

决策逻辑 ：引擎根据聚焦的诊断条目ID，查询其关联的知识点和任务，生成个性化的建议（如“建议你通过这个训练巩固此知识点”）。

状态变更 ：

```typescript
// ui.piopeeIntervention 被更新

ui.piopeeIntervention = {

```
isVisible: true,

type: 'suggestion',

title: '巩固建议',

description: `针对“${diagnosisItem.title}”，建议你完成专项训练。`,

actions: [{

label: '去看看',

callback: () => {

```typescript
// 1. 关闭介入气泡

ui.piopeeIntervention.isVisible = false;

// 2. 导航到对应的训练任务

plan.focusedTask = correspondingTask;

// 3. 打开右侧讲解面板（如果需要）

ui.globalPanels.push({...});

}

}],

```
timeout: 8000

```typescript
};

```
UI渲染 ：PioppeIntervention组件检测到ui.piopeeIntervention.isVisible为true，根据其type、description等属性渲染一个气泡或卡片，并开始倒计时。

### 场景三：从“诊断报告”点击条目跳转到“任务执行”

用户操作 ：在诊断报告界面（L3.4）点击一个诊断条目。

状态变更1 (诊断焦点) ：

```typescript
diagnosis.focusedDiagnosisItemId = clickedItemId; // 触发场景二的PIOPPE规则

```
用户操作 ：点击该诊断条目关联的“去训练”按钮。

状态变更2 (旅程与任务) ：

```typescript
plan.currentJourney = 'practice'; // 切换到训练旅程

plan.focusedTask = correspondingPracticeTask; // 设置聚焦任务为对应的训练任务

```
路由/视图切换 ：应用路由根据plan.currentJourney变化，渲染“任务执行”旅程对应的视图（L1.2, L3.2/L3.3）。

组件初始化 ：PlanNavigator高亮对应的任务。ContentPlayer和GlobalPanel根据plan.focusedTask加载该任务相关的内容和提示。

---

这份《L0：应用全局状态与数据流定义》文档，为开发团队提供了构建应用状态管理的完整蓝图。  它明确了：

数据是什么 ：通过完整的TypeScript接口定义。

数据怎么用 ：通过组件-状态关系图，明确了各组件的职责边界。

数据怎么变 ：通过关键数据流场景，描绘了复杂交互下状态变化的完整链条。

开发团队可据此直接创建状态管理Store，并确保所有组件的行为与L1、L2、L3的设计严格对齐。

如果确认此文档内容清晰、无误，我们可以继续进行下一份文档《L1/L2/L3 设计优化与细则增补（V1.1）》的撰写。请指示。
