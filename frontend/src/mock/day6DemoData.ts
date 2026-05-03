export const demoQuickPrompts = ['我不懂函数单调性', '帮我出几道三角函数题', '导数题总是算错怎么办']

export const demoKnowledgePointNames: Record<string, string> = {
  kp_sin_func: '正弦函数',
  kp_func_mono: '函数单调性',
  kp_derivative_basic: '基本求导法则',
}

export const demoChatScriptByMessage: Record<
  string,
  { reply: string; knowledgePointIds: string[]; taskId: string | null; intent: string }
> = {
  '今天数学课讲了三角函数，有个地方没听懂': {
    reply:
      '我听到你是概念层面的卡点。先确认一下：你是对“正弦函数定义”里角度与函数值的对应关系不清楚吗？我已先为你准备一个小任务，边学边练会更快。',
    knowledgePointIds: ['kp_sin_func'],
    taskId: 'c0000000-0000-0000-0000-000000000003',
    intent: 'CLARIFY_CONCEPT',
  },
}

export const demoDiagnosisReport = {
  title: '高二数学阶段诊断报告（演示）',
  score: { total: 78, full: 100 },
  weaknesses: [
    { id: 'kp_sin_func', name: '正弦函数', mastery: 0.35, recommendation: '优先回顾定义域与图像周期' },
    { id: 'kp_derivative_basic', name: '基本求导法则', mastery: 0.42, recommendation: '强化乘除与链式法则' },
    { id: 'kp_func_mono', name: '函数单调性', mastery: 0.48, recommendation: '结合导数符号做区间判定' },
  ],
}
