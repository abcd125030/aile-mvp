# 实施计划：艾乐学伴 MVP Day 6 — UI 打磨与演示场景准备

## 概述

将 Day 6 设计方案拆解为可执行任务，按“视觉统一 -> 对话增强 -> 状态态完善 -> 响应式优化 -> 演示数据 -> 演练验收”推进。  
当前文档已根据实际开发进度回写状态。

## 任务

- [x] 1. 建立 Day 6 视觉主题与全局样式
  - [x] 1.1 扩展全局主题 Token
    - 在 `frontend/src/index.css` 增加主色、辅色、背景色、语义状态色与通用阴影/圆角变量
    - 统一按钮、卡片、标题、输入框的基础样式类
    - _需求: 1.1, 1.2, 1.3_

  - [x] 1.2 补充艾乐头像与品牌资源位
    - 在 `frontend/src/assets/` 增加艾乐头像占位资源（或默认 SVG）
    - 在 `HomePage`、`DailyClearancePage` 接入统一头像展示与回退逻辑
    - _需求: 2.1, 2.2, 2.3_

- [x] 2. 增强对话体验（`/daily-clearance`）
  - [x] 2.1 实现“思考中”动效
    - 在 `frontend/src/containers/DailyClearancePage.tsx` 将纯文本加载替换为三点跳动组件
    - 与 `useChatStore.isStreaming` 状态联动
    - _需求: 3.1_

  - [x] 2.2 增加快捷问题建议气泡
    - 在 `DailyClearancePage` 增加固定建议列表（至少 2 条）
    - 点击建议后复用现有 `sendMessage` 流程发起提问
    - _需求: 3.2, 3.3_

  - [x] 2.3 接入知识点卡片交互
    - 在 `frontend/src/types/api.ts` 与 `frontend/src/stores/useChatStore.ts` 增补消息 metadata 结构
    - 在 `DailyClearancePage` 为 AI 消息渲染知识点卡片并支持跳转 `/execution`
    - _需求: 4.1, 4.2, 4.3_

- [x] 3. 完善加载态/空态/错误态
  - [x] 3.1 首页与执行页骨架屏
    - 在 `frontend/src/containers/HomePage.tsx`、`ExecutionPage.tsx` 增加骨架屏组件
    - 维持现有数据流，不改变业务调用顺序
    - _需求: 5.1_

  - [x] 3.2 诊断页空态与错误态增强
    - 在 `frontend/src/containers/DiagnosisPage.tsx` 增加统一空态插画位与重试入口
    - 保留“生成巩固计划”主按钮
    - _需求: 5.2, 5.3_

- [x] 4. 页面动效与响应式优化
  - [x] 4.1 增加轻量页面/区块过渡动画
    - 在核心容器页引入轻量 fade/slide 过渡（优先 CSS/Tailwind）
    - 控制动效时长在 150ms~300ms
    - _需求: 6.1, 6.2, 6.3_

  - [x] 4.2 细化平板优先布局
    - 调整 `DailyClearancePage`、`ExecutionPage`、`DiagnosisPage` 在 `md` 断点上下的布局差异
    - 确保 `>=768px` 双栏效率与 `<768px` 纵向可用性
    - _需求: 7.1, 7.2, 7.3_

- [x] 5. 准备 Day 6 演示场景数据与演示模式
  - [x] 5.1 落地场景 A/B/C 数据文件
    - 在 `database/` 下新增 Day 6 场景补充 SQL（用户画像、任务、诊断报告）
    - 确保与现有 DDL 字段兼容（`daily_problems`、`learning_tasks`、`diagnosis_reports`）
    - _需求: 8.1, 8.2, 8.3_

  - [x] 5.2 增加前端演示模式配置
    - 在 `frontend/src/config/` 增加 `Demo_Mode` 开关配置
    - 在 `chatService`/诊断数据读取链路中支持“预置数据优先”策略
    - _需求: 9.1, 9.2, 9.3, 9.4_

  - [x] 5.3 编写演示脚本说明
    - 在项目文档新增 Day 6 场景脚本（A/B/C 的进入方式、操作步骤、预期结果）
    - _需求: 8.4, 10.1_

- [ ] 6. 验证与回归
  - [x] 6.1 前端构建与基础检查
    - 执行 `frontend` 构建，修复新增 UI 改动导致的类型或编译问题
    - _需求: 10.2, 10.3_

  - [ ] 6.2 三场景手动走查
    - 按 A/B/C 脚本逐条验证：入口可达、关键按钮可用、流程无阻塞
    - 记录并修复高优问题
    - 当前状态：代码侧已准备完成，待你本地按脚本手动验收
    - _需求: 10.1, 10.2, 10.3_
