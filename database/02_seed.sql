-- ============================================================
-- 艾乐学伴 MVP — 种子数据脚本
-- 文件: database/02_seed.sql
-- 说明: 插入知识点、练习题、演示用户、学习计划与任务
-- 注意: 使用 ON CONFLICT DO NOTHING 确保可重复执行
-- ============================================================

-- ============================================================
-- 1. 知识点数据（20 条：函数 8 + 三角函数 6 + 导数 6）
-- ============================================================

INSERT INTO knowledge_points (id, name, description, prerequisite_ids, difficulty, subject) VALUES
-- 函数模块（8 个）
('kp_func_def', '函数的概念与表示', '函数的定义、定义域、值域、三种表示法（解析法、列表法、图像法）', '[]', 0.30, 'math'),
('kp_func_mono', '函数的单调性', '函数单调递增、单调递减的定义与判断方法', '["kp_func_def"]', 0.45, 'math'),
('kp_func_parity', '函数的奇偶性', '奇函数与偶函数的定义、判断方法及图像特征', '["kp_func_def"]', 0.45, 'math'),
('kp_comp_func', '复合函数', '复合函数的概念、构造方法与定义域求解', '["kp_func_def"]', 0.55, 'math'),
('kp_comp_func_mono', '复合函数的单调性', '复合函数单调性的判断法则（同增异减）', '["kp_func_mono", "kp_comp_func"]', 0.65, 'math'),
('kp_exp_func', '指数函数', '指数函数的定义、图像、性质及应用', '["kp_func_mono"]', 0.50, 'math'),
('kp_log_func', '对数函数', '对数函数的定义、图像、性质及与指数函数的关系', '["kp_exp_func"]', 0.55, 'math'),
('kp_power_func', '幂函数', '幂函数的定义、常见幂函数的图像与性质', '["kp_func_def"]', 0.45, 'math'),

-- 三角函数模块（6 个）
('kp_trig_def', '三角函数的定义', '任意角的三角函数定义、弧度制、三角函数线', '["kp_func_def"]', 0.40, 'math'),
('kp_sin_func', '正弦函数', '正弦函数的图像、周期性、振幅、相位变换', '["kp_trig_def"]', 0.50, 'math'),
('kp_cos_func', '余弦函数', '余弦函数的图像与性质、与正弦函数的关系', '["kp_trig_def"]', 0.50, 'math'),
('kp_tan_func', '正切函数', '正切函数的图像、性质、定义域与周期', '["kp_trig_def"]', 0.50, 'math'),
('kp_trig_identity', '三角恒等变换', '和差化积、积化和差、二倍角公式、辅助角公式', '["kp_sin_func", "kp_cos_func"]', 0.65, 'math'),
('kp_trig_graph', '三角函数图像与性质', '三角函数图像的平移、伸缩变换及综合性质分析', '["kp_sin_func", "kp_cos_func"]', 0.60, 'math'),

-- 导数模块（6 个）
('kp_derivative_concept', '导数的概念', '导数的定义、几何意义（切线斜率）、物理意义（瞬时速度）', '["kp_func_mono"]', 0.50, 'math'),
('kp_derivative_basic', '基本求导法则', '常见函数的导数公式、四则运算求导法则', '["kp_derivative_concept"]', 0.55, 'math'),
('kp_derivative_chain', '复合函数求导', '链式法则、复合函数的求导方法', '["kp_derivative_basic", "kp_comp_func"]', 0.70, 'math'),
('kp_derivative_mono', '导数与函数单调性', '利用导数符号判断函数的单调区间', '["kp_derivative_basic", "kp_func_mono"]', 0.65, 'math'),
('kp_derivative_extrema', '导数与极值', '极值点的定义、利用导数求极值与最值', '["kp_derivative_mono"]', 0.70, 'math'),
('kp_derivative_app', '导数应用', '导数在实际问题中的应用（最优化问题、曲线切线等）', '["kp_derivative_extrema"]', 0.75, 'math')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 2. 练习题数据（16 道：选择题 11 + 填空题 5）
-- ============================================================

INSERT INTO exercise_items (id, stem, options, correct_answer, solution, knowledge_point_ids, difficulty, metadata) VALUES
-- 选择题（11 道）
('ex_func_001', '下列对应关系中，构成从集合A到集合B的函数的是（）', '["A. A={1,2,3}, B={4,5,6}, f: x→x+3", "B. A=R, B=R, f: x→±√x", "C. A={1,2,3}, B={1,2}, f: x→x", "D. A=R, B=R⁺, f: x→x²"]', 'A', '选项A中，A中每个元素在B中都有唯一对应，满足函数定义。B中对应不唯一，C中3无对应，D中值域不是R⁺。', '["kp_func_def"]', 0.30, '{"type": "choice", "source": "textbook"}'),

('ex_func_002', '函数f(x)=x²-2x在区间[0,3]上的单调递增区间是（）', '["A. [0,1]", "B. [1,3]", "C. [0,3]", "D. [-1,3]"]', 'B', 'f(x)=x²-2x=(x-1)²-1，顶点x=1，在[1,3]上单调递增。', '["kp_func_mono"]', 0.40, '{"type": "choice", "source": "textbook"}'),

('ex_func_003', '已知f(x)是定义在R上的奇函数，且f(2)=1，则f(-2)=（）', '["A. -1", "B. 1", "C. 0", "D. 2"]', 'A', '奇函数满足f(-x)=-f(x)，所以f(-2)=-f(2)=-1。', '["kp_func_parity"]', 0.35, '{"type": "choice", "source": "textbook"}'),

('ex_func_004', '设f(x)=2x+1, g(x)=x², 则f(g(2))=（）', '["A. 7", "B. 9", "C. 25", "D. 5"]', 'B', 'g(2)=4, f(g(2))=f(4)=2×4+1=9。', '["kp_comp_func"]', 0.40, '{"type": "choice", "source": "textbook"}'),

('ex_func_005', '函数y=e^(-x²)的单调递增区间是（）', '["A. (-∞, 0]", "B. [0, +∞)", "C. (-∞, +∞)", "D. [-1, 1]"]', 'A', '令u=-x²，u在(-∞,0]上递增，e^u为增函数，复合函数同增，故在(-∞,0]上递增。', '["kp_comp_func_mono", "kp_exp_func"]', 0.60, '{"type": "choice", "source": "exam"}'),

('ex_trig_001', 'sin(5π/6)的值为（）', '["A. 1/2", "B. -1/2", "C. √3/2", "D. -√3/2"]', 'A', 'sin(5π/6)=sin(π-π/6)=sin(π/6)=1/2。', '["kp_trig_def", "kp_sin_func"]', 0.35, '{"type": "choice", "source": "textbook"}'),

('ex_trig_002', '函数y=2sin(2x+π/3)的最小正周期是（）', '["A. π", "B. 2π", "C. π/2", "D. 4π"]', 'A', 'T=2π/ω=2π/2=π。', '["kp_sin_func", "kp_trig_graph"]', 0.45, '{"type": "choice", "source": "textbook"}'),

('ex_trig_003', 'cos²α - sin²α 等于（）', '["A. cos2α", "B. sin2α", "C. 1", "D. -1"]', 'A', '由二倍角公式cos2α=cos²α-sin²α。', '["kp_trig_identity"]', 0.40, '{"type": "choice", "source": "textbook"}'),

('ex_deriv_001', '函数f(x)=x³在x=1处的导数值为（）', '["A. 1", "B. 2", "C. 3", "D. 4"]', 'C', 'f''(x)=3x², f''(1)=3×1²=3。', '["kp_derivative_concept", "kp_derivative_basic"]', 0.40, '{"type": "choice", "source": "textbook"}'),

('ex_deriv_002', '函数f(x)=x³-3x的单调递减区间是（）', '["A. (-1,1)", "B. (-∞,-1)∪(1,+∞)", "C. (0,+∞)", "D. (-∞,0)"]', 'A', 'f''(x)=3x²-3=3(x+1)(x-1)，f''(x)<0时x∈(-1,1)，故单调递减区间为(-1,1)。', '["kp_derivative_mono"]', 0.55, '{"type": "choice", "source": "exam"}'),

('ex_deriv_003', '函数f(x)=x³-3x²+1在x=0处的切线方程为（）', '["A. y=-3x+1", "B. y=3x+1", "C. y=1", "D. y=-x+1"]', 'C', 'f(0)=1, f''(x)=3x²-6x, f''(0)=0，切线方程为y=1。', '["kp_derivative_concept"]', 0.50, '{"type": "choice", "source": "exam"}'),

-- 填空题（5 道）
('ex_func_fill_001', '函数f(x)=√(x-1)的定义域为______。', NULL, '[1,+∞)', '根号下表达式≥0，即x-1≥0，解得x≥1。', '["kp_func_def"]', 0.30, '{"type": "fill_blank", "source": "textbook"}'),

('ex_func_fill_002', '已知f(x)=ln(x), 则f(e²)=______。', NULL, '2', 'f(e²)=ln(e²)=2。', '["kp_log_func"]', 0.35, '{"type": "fill_blank", "source": "textbook"}'),

('ex_trig_fill_001', '已知sinα=3/5，α为第二象限角，则cosα=______。', NULL, '-4/5', 'sin²α+cos²α=1，cosα=±4/5，第二象限cosα<0，故cosα=-4/5。', '["kp_trig_def"]', 0.45, '{"type": "fill_blank", "source": "textbook"}'),

('ex_deriv_fill_001', '函数f(x)=x⁴-2x²的极小值为______。', NULL, '-1', 'f''(x)=4x³-4x=4x(x²-1)，极值点x=0,±1。f(0)=0, f(±1)=-1，极小值为-1。', '["kp_derivative_extrema"]', 0.60, '{"type": "fill_blank", "source": "exam"}'),

('ex_deriv_fill_002', '曲线y=xe^x在x=0处的切线斜率为______。', NULL, '1', 'y''=(1+x)e^x，y''(0)=(1+0)×1=1。', '["kp_derivative_basic", "kp_derivative_concept"]', 0.55, '{"type": "fill_blank", "source": "exam"}')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 3. 演示用户数据（2 个）
-- ============================================================

-- 使用固定 UUID 确保脚本可重复执行
INSERT INTO users (id, phone, nickname, grade, textbook_version, settings) VALUES
('a0000000-0000-0000-0000-000000000001', '13800000001', '艾学同学', '高二', '人教版A版', '{}'),
('a0000000-0000-0000-0000-000000000002', '13800000002', '小明同学', '高三', '人教版A版', '{}')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 4. 学习计划（为用户 1 创建 1 个 active 计划）
-- ============================================================

INSERT INTO learning_plans (id, user_id, title, status, version) VALUES
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', '函数与导数综合提升计划', 'active', 1)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 5. 学习任务（5 个，覆盖不同 type 和 status）
-- ============================================================

INSERT INTO learning_tasks (id, plan_id, title, type, status, source, knowledge_point_ids, metadata, started_at, completed_at) VALUES
('c0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', '理解函数的概念与三种表示法', 'concept_learning', 'completed', 'scheduled', '["kp_func_def"]', '{}', '2024-01-10 09:00:00+08', '2024-01-10 10:30:00+08'),
('c0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001', '掌握函数单调性的判断方法', 'concept_learning', 'completed', 'scheduled', '["kp_func_mono"]', '{}', '2024-01-11 09:00:00+08', '2024-01-11 10:00:00+08'),
('c0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', '复合函数单调性专项练习', 'practice', 'in_progress', 'scheduled', '["kp_comp_func_mono"]', '{}', '2024-01-12 09:00:00+08', NULL),
('c0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001', '导数的概念与几何意义', 'concept_learning', 'pending', 'scheduled', '["kp_derivative_concept"]', '{}', NULL, NULL),
('c0000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000001', '基本求导法则练习', 'practice', 'pending', 'scheduled', '["kp_derivative_basic"]', '{}', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 6. 更新用户 1 的 current_plan_id
-- ============================================================

UPDATE users
SET current_plan_id = 'b0000000-0000-0000-0000-000000000001'
WHERE id = 'a0000000-0000-0000-0000-000000000001'
  AND current_plan_id IS DISTINCT FROM 'b0000000-0000-0000-0000-000000000001';
