from fastapi import APIRouter, HTTPException
from data.db import get_q_matrix, get_x_matrix, get_knowledge_graph, get_students
from model.dina import DINA
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
dina_model = DINA()

@router.get("/students")
def get_student_list():
    """
    获取所有学生ID列表
    :return: 学生ID列表
    """
    try:
        logger.info("开始获取学生列表")
        
        # 从数据库获取学生列表
        students = get_students()
        logger.info(f"获取到 {len(students)} 个学生")
        
        return {
            "students": students
        }
        
    except Exception as e:
        logger.error(f"获取学生列表时发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

@router.get("/student/{student_id}/knowledge")
def get_student_knowledge(student_id: str):
    """
    获取学生知识点掌握情况（不包含大模型建议，用于快速显示雷达图）
    :param student_id: 学生ID
    :return: 学生知识点掌握概率
    """
    try:
        logger.info(f"开始处理学生 {student_id} 的知识掌握情况请求")
        
        # 1. 从数据库获取Q/X矩阵
        q_matrix = get_q_matrix()
        x_matrix = get_x_matrix(student_id)
        logger.info(f"获取到Q矩阵: {len(q_matrix)} 个题目, X矩阵: {len(x_matrix)} 个作答记录")
        
        # 2. 调用DINA模型计算掌握概率
        mastery_probs = dina_model.predict(student_id, q_matrix, x_matrix)
        logger.info(f"计算得到掌握概率: {mastery_probs}")
        
        # 3. 获取知识图谱
        knowledge_graph = get_knowledge_graph()
        logger.info(f"获取到知识图谱: {len(knowledge_graph)} 个知识点")
        
        # 4. 返回给前端（不包含学习建议，建议通过单独的API获取）
        result = {
            "student_id": student_id,
            "mastery_probs": mastery_probs,
            "knowledge_graph": knowledge_graph,
            "learning_suggestions": []  # 空列表，建议通过单独API获取
        }
        logger.info(f"成功返回学生 {student_id} 的数据")
        return result
        
    except Exception as e:
        logger.error(f"处理学生 {student_id} 的请求时发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

@router.get("/student/{student_id}/suggestions")
def get_student_suggestions(student_id: str):
    """
    获取学生个性化学习建议（单独接口，异步调用大模型）
    :param student_id: 学生ID
    :return: 个性化学习建议
    """
    from model.llm_service import LLMService
    llm_service = LLMService()
    
    try:
        logger.info(f"开始生成学生 {student_id} 的学习建议")
        
        # 1. 获取必要的数据
        q_matrix = get_q_matrix()
        x_matrix = get_x_matrix(student_id)
        mastery_probs = dina_model.predict(student_id, q_matrix, x_matrix)
        knowledge_graph = get_knowledge_graph()
        
        # 2. 生成个性化学习建议
        try:
            learning_suggestions = llm_service.generate_learning_suggestions(student_id, mastery_probs, knowledge_graph)
            logger.info(f"生成学习建议: {learning_suggestions}")
            return {
                "student_id": student_id,
                "learning_suggestions": learning_suggestions
            }
        except Exception as e:
            logger.error(f"生成学习建议失败: {e}")
            return {
                "student_id": student_id,
                "learning_suggestions": [],
                "error": "生成学习建议失败"
            }
        
    except Exception as e:
        logger.error(f"处理学生 {student_id} 的建议请求时发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")