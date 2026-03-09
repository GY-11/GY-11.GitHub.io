import os
import logging
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """大模型服务"""
    
    def __init__(self):
        """
        初始化大模型服务
        从环境变量获取API密钥
        """
        self.api_key = os.getenv('ARK_API_KEY', '6546e540-0839-40d4-ad82-32c7079da542')
        # 火山引擎API地址（根据实际部署区域调整）
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = "ep-m-20260308230924-xmcht"  # 火山引擎模型端点ID
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_learning_suggestions(self, student_id, mastery_probs, knowledge_graph):
        """
        生成个性化学习建议（仅由大模型提供）
        :param student_id: 学生ID
        :param mastery_probs: 知识点掌握概率
        :param knowledge_graph: 知识图谱
        :return: 学习建议列表
        """
        # 构建Prompt
        prompt = f"你是教育AI辅导专家。已知学生ID为{student_id}，其知识点掌握概率为：{mastery_probs}，知识图谱前序关系为：{knowledge_graph}。请生成3条个性化学习建议，要求：\n1. 优先推荐掌握概率低于0.6的知识点；\n2. 结合前序关系，先补基础再学进阶；\n3. 每条建议必须严格按照以下格式输出：\n\n**知识点名称**：[知识点名称]\n**学习重点**：[学习重点内容]\n**推荐题目类型**：[推荐题目类型]\n\n确保每条建议都包含这三个部分，并且格式严格按照上述要求。"
        
        logger.info(f"开始调用大模型API，学生ID: {student_id}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Model: {self.model}")
        
        # 使用OpenAI SDK调用API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"API响应成功")
            
            # 解析响应
            content = response.choices[0].message.content
            logger.info(f"大模型返回内容: {content}")
            
            # 解析返回的内容，提取学习建议
            suggestions = self._parse_suggestions(content)
            logger.info(f"解析后的学习建议: {suggestions}")
            
            if suggestions:
                return suggestions
            else:
                # 如果解析失败，返回默认建议
                logger.warning("解析失败，返回默认学习建议")
                return [
                    {"name": "代数基础", "focus": "重点掌握基本代数运算和方程求解", "type": "基础代数题"},
                    {"name": "函数", "focus": "理解函数概念和基本性质", "type": "函数性质题"},
                    {"name": "导数", "focus": "掌握导数的基本概念和计算方法", "type": "导数计算题"}
                ]
                
        except Exception as e:
            logger.error(f"调用大模型时发生异常: {e}", exc_info=True)
            # 发生异常时返回默认建议
            return [
                {"name": "代数基础", "focus": "重点掌握基本代数运算和方程求解", "type": "基础代数题"},
                {"name": "函数", "focus": "理解函数概念和基本性质", "type": "函数性质题"},
                {"name": "导数", "focus": "掌握导数的基本概念和计算方法", "type": "导数计算题"}
            ]
    
    def _parse_suggestions(self, content):
        """
        解析大模型返回的内容，提取学习建议
        :param content: 大模型返回的文本内容
        :return: 学习建议列表
        """
        import re

        suggestions = []

        content = content.strip()

        # 清理内容，移除不必要的格式
        content = re.sub(r'---+', '', content)
        content = re.sub(r'#### 建议\d+', '', content)
        content = re.sub(r'\n+', '\n', content)

        # 尝试匹配按行分隔的格式
        lines = content.split('\n')
        current_suggestion = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配知识点名称
            if line.startswith('**知识点名称**：'):
                if current_suggestion and len(current_suggestion) == 3:
                    suggestions.append(current_suggestion)
                name = line.replace('**知识点名称**：', '').strip()
                # 移除可能的多余符号
                name = re.sub(r'[\-\s]+$', '', name)
                current_suggestion = {"name": name}
                
            # 匹配学习重点
            elif line.startswith('**学习重点**：'):
                focus = line.replace('**学习重点**：', '').strip()
                # 移除可能的多余符号
                focus = re.sub(r'[\-\s]+$', '', focus)
                current_suggestion["focus"] = focus
                
            # 匹配推荐题目类型
            elif line.startswith('**推荐题目类型**：'):
                type_ = line.replace('**推荐题目类型**：', '').strip()
                # 移除可能的多余符号
                type_ = re.sub(r'[\-\s]+$', '', type_)
                current_suggestion["type"] = type_
                
                if len(current_suggestion) == 3:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}

        # 添加最后一个建议
        if current_suggestion and len(current_suggestion) == 3:
            suggestions.append(current_suggestion)

        return suggestions[:3] if suggestions else []