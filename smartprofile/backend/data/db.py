import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect('smartprofile.db')
        conn.row_factory = sqlite3.Row
        logger.info("数据库连接成功")
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def get_q_matrix():
    """返回Q矩阵"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询Q矩阵数据
    cursor.execute("SELECT question_id, kp_id, is_examined FROM q_matrix")
    rows = cursor.fetchall()
    
    # 构建Q矩阵字典
    q_matrix = {}
    for row in rows:
        question_id = row['question_id']
        kp_id = row['kp_id']
        is_examined = row['is_examined']
        
        if question_id not in q_matrix:
            q_matrix[question_id] = {}
        q_matrix[question_id][kp_id] = is_examined
    
    conn.close()
    return q_matrix

def get_x_matrix(student_id):
    """返回某学生的X矩阵"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询学生作答数据
    cursor.execute(
        "SELECT question_id, is_correct FROM x_matrix WHERE student_id = ?",
        (student_id,)
    )
    rows = cursor.fetchall()
    
    # 构建X矩阵字典
    x_matrix = {}
    for row in rows:
        question_id = row['question_id']
        is_correct = row['is_correct']
        x_matrix[question_id] = is_correct
    
    conn.close()
    return x_matrix

def get_knowledge_graph():
    """返回知识点前序/后继关系"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询知识点数据
    cursor.execute("SELECT kp_id, name, prerequisite_kp_id FROM knowledge_points")
    rows = cursor.fetchall()
    
    # 构建知识图谱
    knowledge_graph = {}
    for row in rows:
        kp_id = row['kp_id']
        name = row['name']
        prerequisite_kp_id = row['prerequisite_kp_id']
        
        knowledge_graph[kp_id] = {
            'name': name,
            'prerequisite': prerequisite_kp_id,
            'successors': []
        }
    
    # 填充后继关系
    for kp_id, info in knowledge_graph.items():
        prerequisite = info['prerequisite']
        if prerequisite:
            knowledge_graph[prerequisite]['successors'].append(kp_id)
    
    conn.close()
    return knowledge_graph

def get_students():
    """返回所有学生ID列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询所有唯一的学生ID
    cursor.execute("SELECT DISTINCT student_id FROM x_matrix ORDER BY student_id")
    rows = cursor.fetchall()
    
    # 提取学生ID列表
    students = [row['student_id'] for row in rows]
    
    conn.close()
    return students