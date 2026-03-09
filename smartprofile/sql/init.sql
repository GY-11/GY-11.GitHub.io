-- 知识点表（含前序关系）
CREATE TABLE knowledge_points (
    kp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    prerequisite_kp_id TEXT  -- 前序知识点ID
);

-- Q矩阵：题目-知识点关联
CREATE TABLE q_matrix (
    question_id TEXT,
    kp_id TEXT,
    is_examined INTEGER DEFAULT 1,  -- 0/1表示是否考察
    PRIMARY KEY (question_id, kp_id)
);

-- X矩阵：学生-题目作答
CREATE TABLE x_matrix (
    student_id TEXT,
    question_id TEXT,
    is_correct INTEGER,  -- 0=错，1=对
    answer_time DATETIME,
    PRIMARY KEY (student_id, question_id)
);