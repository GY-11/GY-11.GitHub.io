import sqlite3
import random
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('smartprofile.db')
cursor = conn.cursor()

# 读取并执行建表SQL
with open('init.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
cursor.executescript(sql)

# 知识点数据
knowledge_points = [
    {'kp_id': 'kp1', 'name': '代数基础', 'prerequisite_kp_id': None},
    {'kp_id': 'kp2', 'name': '函数', 'prerequisite_kp_id': 'kp1'},
    {'kp_id': 'kp3', 'name': '导数', 'prerequisite_kp_id': 'kp2'},
    {'kp_id': 'kp4', 'name': '积分', 'prerequisite_kp_id': 'kp3'},
    {'kp_id': 'kp5', 'name': '微分方程', 'prerequisite_kp_id': 'kp3'}
]

# 插入知识点
for kp in knowledge_points:
    cursor.execute(
        "INSERT INTO knowledge_points (kp_id, name, prerequisite_kp_id) VALUES (?, ?, ?)",
        (kp['kp_id'], kp['name'], kp['prerequisite_kp_id'])
    )

# 生成20道题目，每道题关联1-2个知识点
questions = []
for i in range(1, 21):
    question_id = f'q{i}'
    # 随机选择1-2个知识点
    kp_count = random.randint(1, 2)
    selected_kps = random.sample([kp['kp_id'] for kp in knowledge_points], kp_count)
    questions.append((question_id, selected_kps))

# 插入Q矩阵数据
for question_id, kp_ids in questions:
    for kp_id in kp_ids:
        cursor.execute(
            "INSERT INTO q_matrix (question_id, kp_id, is_examined) VALUES (?, ?, ?)",
            (question_id, kp_id, 1)
        )

# 生成10名学生
students = [f'student{i}' for i in range(1, 11)]

# 生成学生作答数据
for student_id in students:
    for question_id, _ in questions:
        is_correct = random.randint(0, 1)
        answer_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO x_matrix (student_id, question_id, is_correct, answer_time) VALUES (?, ?, ?, ?)",
            (student_id, question_id, is_correct, answer_time)
        )

# 提交并关闭连接
conn.commit()
conn.close()
print("模拟数据生成完成！")